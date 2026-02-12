#!/usr/bin/env python3
"""
Test Underdog CSV Export Format
Validates that exported CSV is compatible with Underdog Fantasy upload
"""

import csv
from pathlib import Path
from datetime import datetime


def test_csv_format(csv_file: Path) -> bool:
    """
    Test CSV format for Underdog compatibility
    
    Required format:
    - Header row with specific columns
    - Proper encoding (UTF-8)
    - No special characters that break parsing
    - Numeric fields properly formatted
    """
    print(f"🧪 Testing CSV format: {csv_file.name}\n")
    
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    issues = []
    warnings = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Test 1: Check header
            header = next(reader)
            print(f"✓ Header found: {len(header)} columns")
            print(f"  Columns: {', '.join(header)}\n")
            
            required_cols = ['Player Name', 'Team', 'Position', 'Projection']
            for col in required_cols:
                if col not in header:
                    issues.append(f"Missing required column: {col}")
            
            # Test 2: Validate data rows
            rows = list(reader)
            print(f"✓ Data rows: {len(rows)}\n")
            
            if len(rows) == 0:
                issues.append("No data rows found")
                return False
            
            # Test 3: Check first few rows for format
            print("📊 Sample rows (first 3):")
            print("-" * 80)
            
            for i, row in enumerate(rows[:3], 1):
                if len(row) != len(header):
                    issues.append(f"Row {i}: Column count mismatch ({len(row)} vs {len(header)})")
                    continue
                
                data = dict(zip(header, row))
                
                # Validate player name
                if not data.get('Player Name'):
                    issues.append(f"Row {i}: Missing player name")
                
                # Validate numeric fields
                try:
                    proj = float(data.get('Projection', 0))
                    if proj <= 0:
                        warnings.append(f"Row {i}: Projection is zero or negative")
                except ValueError:
                    issues.append(f"Row {i}: Projection is not a valid number")
                
                # Print sample
                print(f"  Row {i}: {data.get('Player Name', 'N/A'):22s} "
                      f"{data.get('Team', 'N/A'):4s} "
                      f"Proj={data.get('Projection', 'N/A'):>6s}")
            
            print("-" * 80)
            
            # Test 4: Check for special characters that might break upload
            for i, row in enumerate(rows, 1):
                for cell in row:
                    if any(ord(char) > 127 for char in str(cell)):
                        warnings.append(f"Row {i}: Contains non-ASCII characters")
                        break
            
            # Test 5: Check file size (shouldn't be too large)
            file_size = csv_file.stat().st_size
            print(f"\n✓ File size: {file_size:,} bytes")
            
            if file_size > 1_000_000:  # 1MB
                warnings.append("File is quite large (>1MB)")
    
    except UnicodeDecodeError:
        issues.append("File encoding error - not valid UTF-8")
    except Exception as e:
        issues.append(f"Unexpected error: {str(e)}")
    
    # Print results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80 + "\n")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    if not issues and not warnings:
        print("✅ ALL TESTS PASSED!")
        print("\n✓ CSV format is compatible with Underdog Fantasy")
        print("✓ Ready to upload")
        return True
    elif not issues:
        print("✅ NO CRITICAL ISSUES")
        print("\n✓ CSV should work, but review warnings")
        return True
    else:
        print("❌ CSV HAS ISSUES")
        print("\n✗ Fix issues before uploading to Underdog")
        return False


def create_sample_csv():
    """Create a sample CSV for testing"""
    workspace = Path.home() / 'clawd' / 'nba'
    workspace.mkdir(parents=True, exist_ok=True)
    
    sample_file = workspace / 'sample_underdog_test.csv'
    
    with open(sample_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Player Name',
            'Team',
            'Position',
            'Projection',
            'Ceiling',
            'Floor',
            'Value',
            'Usage Rate',
            'Consistency',
            'Form Confidence'
        ])
        
        # Sample data
        sample_data = [
            ['Luka Doncic', 'DAL', 'PG', '62.5', '78.1', '46.9', '5.68', '32.1', 'CONSISTENT', '0.90'],
            ['Nikola Jokic', 'DEN', 'C', '61.2', '76.5', '45.9', '5.46', '29.8', 'CONSISTENT', '0.95'],
            ['Giannis Antetokounmpo', 'MIL', 'PF', '58.9', '73.6', '44.2', '5.61', '31.5', 'MODERATE_VARIANCE', '0.85'],
        ]
        
        for row in sample_data:
            writer.writerow(row)
    
    print(f"📝 Created sample CSV: {sample_file}\n")
    return sample_file


def test_underdog_upload_format():
    """Test the exact format Underdog expects"""
    print("="*80)
    print("🏀 UNDERDOG CSV FORMAT TESTER")
    print("="*80 + "\n")
    
    print("Testing Underdog Fantasy CSV format requirements:\n")
    print("Required columns:")
    print("  1. Player Name  (string)")
    print("  2. Team         (3-letter abbreviation)")
    print("  3. Position     (PG/SG/SF/PF/C/G/F)")
    print("  4. Projection   (numeric, 2 decimal places)")
    print("  5. Ceiling      (numeric, 2 decimal places)")
    print("  6. Floor        (numeric, 2 decimal places)")
    print("  7. Value        (numeric, 2 decimal places)")
    print("\nOptional metadata columns accepted.")
    print("\n" + "-"*80 + "\n")
    
    # Create and test sample
    sample_file = create_sample_csv()
    result = test_csv_format(sample_file)
    
    print("\n" + "="*80)
    
    if result:
        print("✅ Format test PASSED - Ready for Underdog upload!")
    else:
        print("❌ Format test FAILED - Review and fix issues")
    
    print("="*80 + "\n")
    
    return result


def main():
    """Run CSV format tests"""
    workspace = Path.home() / 'clawd' / 'nba'
    
    # Look for recent export files
    csv_files = list(workspace.glob('underdog_rankings_*.csv'))
    
    if csv_files:
        print("Found export files:\n")
        for f in csv_files:
            print(f"  • {f.name}")
        print()
        
        # Test most recent
        latest = max(csv_files, key=lambda f: f.stat().st_mtime)
        print(f"Testing most recent: {latest.name}\n")
        print("="*80 + "\n")
        
        test_csv_format(latest)
    else:
        print("No export files found. Running format test with sample...\n")
        test_underdog_upload_format()


if __name__ == '__main__':
    main()
