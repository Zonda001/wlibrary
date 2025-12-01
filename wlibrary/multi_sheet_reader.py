"""
Multi-Sheet Reader - Processing Multiple Sheets in One File
============================================================

Automatically processes all sheets in an Excel file and extracts
structured data from each one.
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd

from .smart_reader import smart_read, SmartStructure
from .reader import get_sheets

logger = logging.getLogger(__name__)


class MultiSheetStructure:
    """Structure for storing data from multiple sheets."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.sheets = {}  # {sheet_name: SmartStructure}
        self.all_metadata = []  # List of metadata from all sheets
        self.all_items = []  # All items from all sheets
        self.sheet_names = []  # Sheet names

    def add_sheet(self, sheet_name: str, structure: SmartStructure):
        """Add structure from a sheet."""
        self.sheets[sheet_name] = structure
        self.sheet_names.append(sheet_name)

        # Add metadata
        if structure.metadata:
            metadata_with_sheet = structure.metadata.copy()
            metadata_with_sheet['sheet_name'] = sheet_name
            metadata_with_sheet['source_file'] = self.file_name
            self.all_metadata.append(metadata_with_sheet)

        # Add items
        for item in structure.items:
            item_with_sheet = item.copy()
            item_with_sheet['sheet_name'] = sheet_name
            item_with_sheet['source_file'] = self.file_name
            item_with_sheet['project_name'] = structure.metadata.get('project_name')
            self.all_items.append(item_with_sheet)

    def get_sheet(self, sheet_name: str) -> Optional[SmartStructure]:
        """Get structure of a specific sheet."""
        return self.sheets.get(sheet_name)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'file_name': self.file_name,
            'file_path': self.file_path,
            'sheet_count': len(self.sheets),
            'sheet_names': self.sheet_names,
            'all_metadata': self.all_metadata,
            'all_items': self.all_items,
            'sheets': {
                name: structure.to_dict()
                for name, structure in self.sheets.items()
            }
        }

    def get_summary(self) -> Dict:
        """Get summary information."""
        total_projects = len(self.all_metadata)
        total_items = len(self.all_items)

        # Calculate costs
        total_cost = 0
        total_advance = 0
        total_remaining = 0

        for meta in self.all_metadata:
            try:
                cost = meta.get('total_cost', '0').replace(' ', '').replace('$', '')
                total_cost += float(cost) if cost else 0
            except:
                pass

            try:
                advance = meta.get('advance', '0').replace(' ', '').replace('$', '')
                total_advance += float(advance) if advance else 0
            except:
                pass

            try:
                remaining = meta.get('remaining', '0').replace(' ', '').replace('$', '')
                total_remaining += float(remaining) if remaining else 0
            except:
                pass

        return {
            'file': self.file_name,
            'total_sheets': len(self.sheets),
            'total_projects': total_projects,
            'total_items': total_items,
            'total_cost': total_cost,
            'total_advance': total_advance,
            'total_remaining': total_remaining,
            'projects': [
                {
                    'sheet': meta.get('sheet_name'),
                    'project': meta.get('project_name'),
                    'client': meta.get('client'),
                    'cost': meta.get('total_cost')
                }
                for meta in self.all_metadata
            ]
        }


def smart_read_all_sheets(file_path: str, skip_empty: bool = True) -> MultiSheetStructure:
    """
    Smart reading of all sheets in an Excel file.

    Automatically processes each sheet separately and extracts structure.

    Args:
        file_path: Path to Excel file
        skip_empty: Skip empty sheets

    Returns:
        MultiSheetStructure with data from all sheets

    Example:
        >>> multi = smart_read_all_sheets("Closed Objects.xlsx")
        >>> print(f"Found {len(multi.sheets)} projects")
        >>> for sheet_name, structure in multi.sheets.items():
        ...     print(f"{sheet_name}: {structure.metadata['project_name']}")
    """
    logger.info(f"Reading all sheets from: {file_path}")

    # Get list of sheets
    try:
        sheet_names = get_sheets(file_path)
        logger.info(f"Found {len(sheet_names)} sheets")
    except Exception as e:
        logger.error(f"Error reading sheets: {e}")
        raise

    # Create structure
    multi_structure = MultiSheetStructure(file_path)

    # Process each sheet
    for sheet_name in sheet_names:
        logger.info(f"Processing sheet: {sheet_name}")

        try:
            # Read sheet
            structure = smart_read(file_path, sheet_name=sheet_name)

            # Check if not empty
            if skip_empty:
                if structure.table_data is None or len(structure.table_data) == 0:
                    logger.info(f"  Skipping empty sheet: {sheet_name}")
                    continue

                if not structure.metadata and len(structure.items) == 0:
                    logger.info(f"  Skipping sheet with no data: {sheet_name}")
                    continue

            # Add to multi-structure
            multi_structure.add_sheet(sheet_name, structure)

            logger.info(f"  {sheet_name}: {len(structure.items)} items")
            if structure.metadata:
                logger.info(f"     Project: {structure.metadata.get('project_name', 'N/A')}")

        except Exception as e:
            logger.error(f"  Error processing sheet '{sheet_name}': {e}")
            continue

    logger.info(f"Successfully processed {len(multi_structure.sheets)} sheets")

    return multi_structure


def export_multi_sheet_summary(multi_structure: MultiSheetStructure, output_path: str):
    """
    Create summary report from all sheets.

    Args:
        multi_structure: MultiSheetStructure with data
        output_path: Path to save report
    """
    import json
    from pathlib import Path

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = multi_structure.get_summary()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported summary to: {output_path}")


def export_multi_sheet_to_excel(multi_structure: MultiSheetStructure, output_path: str):
    """
    Export all sheets to one Excel file.

    Each project = separate sheet with its data.
    Additional "Summary" sheet with general information.

    Args:
        multi_structure: MultiSheetStructure with data
        output_path: Path to save file
    """
    import pandas as pd
    from pathlib import Path

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary = multi_structure.get_summary()
        summary_df = pd.DataFrame(summary['projects'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Each project - separate sheet
        for sheet_name, structure in multi_structure.sheets.items():
            if structure.table_data is not None and len(structure.table_data) > 0:
                # Limit sheet name length (Excel limitation - 31 characters)
                safe_sheet_name = sheet_name[:31]
                structure.table_data.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        # All items together
        if multi_structure.all_items:
            all_items_df = pd.DataFrame(multi_structure.all_items)
            all_items_df.to_excel(writer, sheet_name='All_Items', index=False)

    logger.info(f"Exported to Excel: {output_path}")


def compare_projects(multi_structure: MultiSheetStructure) -> pd.DataFrame:
    """
    Compare projects from different sheets.

    Returns:
        DataFrame with comparison table
    """
    import pandas as pd

    comparison = []

    for meta in multi_structure.all_metadata:
        sheet_name = meta.get('sheet_name')
        structure = multi_structure.get_sheet(sheet_name)

        try:
            cost = float(meta.get('total_cost', '0').replace(' ', '').replace('$', ''))
        except:
            cost = 0

        try:
            advance = float(meta.get('advance', '0').replace(' ', '').replace('$', ''))
        except:
            advance = 0

        comparison.append({
            'Sheet': sheet_name,
            'Project': meta.get('project_name'),
            'Client': meta.get('client'),
            'Deadline': meta.get('deadline'),
            'Cost': cost,
            'Advance': advance,
            'Remaining': cost - advance,
            'Items': len(structure.items) if structure else 0,
            'Categories': len(structure.categories) if structure else 0,
        })

    return pd.DataFrame(comparison)