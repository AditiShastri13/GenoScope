import csv
from io import StringIO

def parse_fasta(fasta_content: str) -> str:
    """
    Parse FASTA file content and extract sequence
    
    Args:
        fasta_content: Raw content of a FASTA file
        
    Returns:
        The extracted DNA sequence as a string
        
    Raises:
        ValueError: If the FASTA file is invalid or empty
    """
    if not fasta_content or not isinstance(fasta_content, str):
        raise ValueError("Empty or invalid FASTA content")
        
    lines = fasta_content.strip().split('\n')
    
    # Check for empty file
    if not lines:
        raise ValueError("Empty FASTA file")
    
    # Check if the file seems to be in FASTA format
    has_header = False
    for line in lines:
        if line.startswith('>'):
            has_header = True
            break
    
    if not has_header:
        raise ValueError("Invalid FASTA format: missing header line starting with '>'")
    
    # Parse the sequence
    sequence = ''
    in_sequence = False
    current_sequence = ''
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('>'):
            # New sequence header
            if in_sequence:
                # If we already have a sequence, return it
                # (we only process the first sequence in multi-sequence files)
                return current_sequence
            in_sequence = True
        else:
            # This is sequence data
            if in_sequence:
                current_sequence += line.strip()
    
    # Return the sequence if we found one
    if current_sequence:
        return current_sequence
    
    raise ValueError("No sequence data found in FASTA file")

def parse_csv(csv_content: str) -> str:
    """
    Parse CSV file content and extract sequence
    
    Supports various column names for genetic sequences and handles
    common CSV formatting issues.
    """
    if not csv_content.strip():
        raise ValueError("CSV content is empty")
    
    # Try to detect dialect for better CSV parsing
    try:
        dialect = csv.Sniffer().sniff(csv_content[:1024])
        has_header = csv.Sniffer().has_header(csv_content[:1024])
    except csv.Error:
        # If detection fails, use default Excel dialect
        dialect = 'excel'
        has_header = True
    
    # Common column names that might contain genetic sequences
    sequence_column_names = [
        'sequence', 'dna_sequence', 'genetic_sequence', 'dna', 
        'nucleotides', 'bases', 'seq', 'gene_sequence'
    ]
    
    # First try as a dict reader (with headers)
    if has_header:
        try:
            csv_reader = csv.DictReader(StringIO(csv_content), dialect=dialect)
            rows = list(csv_reader)
            
            if not rows:
                raise ValueError("CSV file contains no data rows")
                
            # Check for known column names
            for row in rows:
                # Case insensitive search for column names
                normalized_columns = {k.lower(): v for k, v in row.items()}
                
                for column_name in sequence_column_names:
                    if column_name in normalized_columns:
                        sequence = normalized_columns[column_name]
                        if sequence and isinstance(sequence, str):
                            return sequence.strip()
            
            # If no matching columns, check the first non-empty value in the first row
            for value in row.values():
                if value and isinstance(value, str) and len(value) >= 20:  # Likely a sequence
                    return value.strip()
        except Exception as e:
            # If dict reading fails, we'll try the next method
            pass
    
    # Try as a regular CSV reader
    try:
        csv_reader = csv.reader(StringIO(csv_content), dialect=dialect)
        rows = list(csv_reader)
        
        if not rows:
            raise ValueError("CSV file contains no data rows")
        
        if has_header:
            header = rows[0]
            data_rows = rows[1:]
            
            # Try to find a column with sequence-like header
            for col_idx, col_name in enumerate(header):
                if any(seq_name in col_name.lower() for seq_name in sequence_column_names):
                    for row in data_rows:
                        if col_idx < len(row) and row[col_idx]:
                            return row[col_idx].strip()
        
        # Last resort: return first non-empty cell that looks like a sequence
        # Skip header if it exists
        start_row = 1 if has_header else 0
        
        for row in rows[start_row:]:
            for cell in row:
                # Check if the cell looks like a genetic sequence
                if cell and isinstance(cell, str) and len(cell) >= 20:
                    # Basic heuristic: Sequences have high percentage of ATCG
                    dna_chars = sum(c.upper() in 'ATCG' for c in cell)
                    if dna_chars / len(cell) > 0.8:  # 80% of characters are ATCG
                        return cell.strip()
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")
    
    raise ValueError("No valid genetic sequence found in CSV file")

def validate_genetic_sequence(sequence: str) -> bool:
    """
    Validate if the sequence contains only valid DNA nucleotides and meets
    quality criteria. Handles common issues in genetic sequences.
    
    Args:
        sequence: The DNA sequence to validate
        
    Returns:
        bool: True if the sequence is valid, False otherwise
    """
    # Handle None or empty sequences
    if not sequence or not isinstance(sequence, str):
        return False
    
    # Strip whitespace and line breaks that might appear in the sequence
    sequence = ''.join(sequence.split())
    
    # Check for empty sequence after cleaning
    if not sequence:
        return False
    
    # Check sequence length (should be reasonable)
    if len(sequence) < 10:
        return False
    
    # Allow for standard nucleotides plus ambiguity codes
    # A, T, G, C - standard nucleotides
    # N - any base
    # R - A or G (purine)
    # Y - C or T (pyrimidine)
    # etc. (IUPAC nucleotide codes)
    valid_chars = set('ATCGNRYSWKMBDHVatcgnryswkmbdhv')
    
    # Count valid characters
    valid_count = sum(char in valid_chars for char in sequence)
    
    # Require at least 95% of characters to be valid nucleotides
    # This allows for some potential sequencing errors
    if valid_count / len(sequence) < 0.95:
        return False
    
    # Ensure the sequence has diversity and isn't just repeats
    # Check if any nucleotide makes up more than 95% of the sequence
    for nucleotide in 'ATCG':
        if sequence.upper().count(nucleotide) / len(sequence) > 0.95:
            return False
            
    # Check for excessive ambiguity codes (N's)
    if sequence.upper().count('N') / len(sequence) > 0.1:  # More than 10% unknown bases
        return False
        
    return True
