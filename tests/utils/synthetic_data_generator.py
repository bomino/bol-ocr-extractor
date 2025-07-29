"""
Synthetic BOL PDF and test data generator for comprehensive testing
"""

import os
import json
import random
import tempfile
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import io

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

@dataclass
class SyntheticBOLData:
    """Ground truth data for synthetic BOL"""
    filename: str
    bol_number: str
    shipper_name: str
    shipper_address: str
    consignee_name: str
    consignee_address: str
    notify_party_name: str = ""
    notify_party_address: str = ""
    vessel_name: str = ""
    voyage_number: str = ""
    port_of_load: str = ""
    port_of_discharge: str = ""
    description_of_goods: str = ""
    quantity_packages: str = ""
    gross_weight: str = ""
    net_weight: str = ""
    freight_terms: str = ""
    date_of_issue: str = ""
    pdf_type: str = "text"  # "text" or "scanned"
    quality: str = "high"   # "high", "medium", "low"
    layout_style: str = "standard"  # "standard", "alternate", "compact"

class SyntheticBOLGenerator:
    """Generates synthetic BOL PDFs with known ground truth data"""
    
    def __init__(self):
        self.sample_data = self._load_sample_data()
        self.layouts = self._define_layouts()
    
    def _load_sample_data(self) -> Dict:
        """Load sample data for generating realistic BOLs"""
        return {
            "shipping_companies": [
                "ABC Shipping Lines Ltd", "Global Maritime Corporation", "Ocean Express Logistics",
                "Pacific Cargo Solutions", "Atlantic Shipping Inc", "Maritime Logistics LLC",
                "Trans-Pacific Lines", "International Cargo Co", "SeaLink Shipping Services",
                "Harbor Express Inc", "Continental Freight Lines", "Oceanic Transport Corp"
            ],
            "consignees": [
                "Import Solutions International", "Trade Partners Limited", "Global Imports Corporation",
                "Destination Logistics Inc", "Harbor Receivers Company", "Port Authority Trading",
                "Customs Clearance Services", "Freight Forwarding Solutions", "Import Export Hub",
                "Distribution Center LLC", "Warehouse Logistics Inc", "Supply Chain Partners"
            ],
            "vessels": [
                "MV Ocean Pioneer", "SS Cargo Master", "MV Pacific Express", "MS Atlantic Carrier",
                "MV Global Voyager", "SS Maritime Explorer", "MV Trade Wind", "MS Sea Navigator",
                "MV Cargo Champion", "SS Pacific Trader", "MV Ocean Gateway", "MS Container King"
            ],
            "ports": [
                "Los Angeles, CA", "New York, NY", "Long Beach, CA", "Savannah, GA",
                "Seattle, WA", "Houston, TX", "Norfolk, VA", "Charleston, SC",
                "Oakland, CA", "Miami, FL", "Boston, MA", "Tacoma, WA"
            ],
            "cargo_types": [
                "Electronic Equipment and Components", "Automotive Parts and Accessories", 
                "Textiles and Apparel Products", "Machinery and Industrial Equipment",
                "Consumer Goods and Appliances", "Industrial Raw Materials", "Food Products and Beverages",
                "Chemical Products and Substances", "Steel and Metal Products", "Pharmaceutical Supplies",
                "Construction Materials", "Paper and Packaging Materials"
            ],
            "addresses": [
                "123 Industrial Boulevard, Suite 100", "456 Harbor Drive, Building A",
                "789 Trade Center Way, Floor 5", "321 Shipping Lane, Unit 200",
                "654 Commerce Street, Suite 50", "987 Export Avenue, Building B",
                "147 Logistics Park, Unit 300", "258 Freight Terminal, Bay 4",
                "369 Container Yard, Section C", "741 Port Access Road, Gate 2"
            ],
            "cities_states": [
                ("Los Angeles", "CA", "90001"), ("New York", "NY", "10001"),
                ("Houston", "TX", "77001"), ("Chicago", "IL", "60601"),
                ("Miami", "FL", "33101"), ("Seattle", "WA", "98101"),
                ("Atlanta", "GA", "30301"), ("Boston", "MA", "02101")
            ]
        }
    
    def _define_layouts(self) -> List[Dict]:
        """Define different BOL layout templates"""
        return [
            {
                "name": "standard_layout",
                "title_pos": (72, 750),
                "bol_number_pos": (400, 720),
                "shipper_pos": (72, 650),
                "consignee_pos": (320, 650),
                "notify_pos": (72, 550),
                "vessel_pos": (320, 550),
                "ports_pos": (72, 450),
                "cargo_pos": (72, 350),
                "weights_pos": (320, 350),
                "date_pos": (72, 250)
            },
            {
                "name": "alternate_layout",
                "title_pos": (100, 720),
                "bol_number_pos": (72, 680),
                "shipper_pos": (72, 600),
                "consignee_pos": (72, 500),
                "notify_pos": (320, 600),
                "vessel_pos": (320, 520),
                "ports_pos": (72, 400),
                "cargo_pos": (72, 300),
                "weights_pos": (320, 300),
                "date_pos": (72, 200)
            },
            {
                "name": "compact_layout",
                "title_pos": (72, 730),
                "bol_number_pos": (400, 730),
                "shipper_pos": (72, 680),
                "consignee_pos": (300, 680),
                "notify_pos": (72, 600),
                "vessel_pos": (300, 600),
                "ports_pos": (72, 520),
                "cargo_pos": (72, 440),
                "weights_pos": (300, 440),
                "date_pos": (72, 360)
            }
        ]
    
    def generate_random_bol_data(self, bol_id: str = None) -> SyntheticBOLData:
        """Generate random but realistic BOL data"""
        if not bol_id:
            bol_id = f"BOL{random.randint(100000, 999999)}"
        
        # Generate random address
        def generate_address():
            address = random.choice(self.sample_data["addresses"])
            city, state, zip_code = random.choice(self.sample_data["cities_states"])
            return f"{address}\\n{city}, {state} {zip_code}"
        
        # Generate random date within last year
        start_date = datetime.now() - timedelta(days=365)
        random_date = start_date + timedelta(days=random.randint(0, 365))
        date_formats = [
            lambda d: d.strftime("%d/%m/%Y"),
            lambda d: d.strftime("%m-%d-%Y"),
            lambda d: d.strftime("%d %b %Y"),
            lambda d: d.strftime("%B %d, %Y")
        ]
        formatted_date = random.choice(date_formats)(random_date)
        
        data = SyntheticBOLData(
            filename=f"synthetic_bol_{bol_id}.pdf",
            bol_number=bol_id,
            shipper_name=random.choice(self.sample_data["shipping_companies"]),
            shipper_address=generate_address(),
            consignee_name=random.choice(self.sample_data["consignees"]),
            consignee_address=generate_address(),
            notify_party_name=random.choice(self.sample_data["consignees"]),
            notify_party_address=generate_address(),
            vessel_name=random.choice(self.sample_data["vessels"]),
            voyage_number=f"VOY{random.randint(2024, 2025)}{random.randint(100, 999)}",
            port_of_load=random.choice(self.sample_data["ports"]),
            port_of_discharge=random.choice(self.sample_data["ports"]),
            description_of_goods=random.choice(self.sample_data["cargo_types"]),
            quantity_packages=f"{random.randint(10, 500)} {random.choice(['CTNS', 'BOXES', 'PALLETS', 'PIECES'])}",
            gross_weight=f"{random.randint(1000, 25000):,} {random.choice(['KG', 'LBS', 'MT'])}",
            net_weight=f"{random.randint(800, 20000):,} {random.choice(['KG', 'LBS', 'MT'])}",
            freight_terms=random.choice(["PREPAID", "COLLECT", "PAYABLE"]),
            date_of_issue=formatted_date,
            layout_style=random.choice(["standard", "alternate", "compact"])
        )
        
        return data
    
    def generate_text_based_pdf(self, bol_data: SyntheticBOLData) -> bytes:
        """Generate text-based PDF with extractable text"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_simple_text_pdf(bol_data)
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        layout = next((l for l in self.layouts if l["name"] == f"{bol_data.layout_style}_layout"), self.layouts[0])
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(layout["title_pos"][0], layout["title_pos"][1], "BILL OF LADING")
        
        # BOL Number
        c.setFont("Helvetica-Bold", 12)
        c.drawString(layout["bol_number_pos"][0], layout["bol_number_pos"][1], f"B/L NO: {bol_data.bol_number}")
        
        # Shipper section
        self._draw_section(c, layout["shipper_pos"], "SHIPPER", bol_data.shipper_name, bol_data.shipper_address)
        
        # Consignee section
        self._draw_section(c, layout["consignee_pos"], "CONSIGNEE", bol_data.consignee_name, bol_data.consignee_address)
        
        # Notify party section
        if bol_data.notify_party_name:
            self._draw_section(c, layout["notify_pos"], "NOTIFY PARTY", bol_data.notify_party_name, bol_data.notify_party_address)
        
        # Vessel information
        c.setFont("Helvetica-Bold", 10)
        c.drawString(layout["vessel_pos"][0], layout["vessel_pos"][1], f"VESSEL: {bol_data.vessel_name}")
        c.drawString(layout["vessel_pos"][0], layout["vessel_pos"][1] - 15, f"VOYAGE: {bol_data.voyage_number}")
        
        # Port information
        c.drawString(layout["ports_pos"][0], layout["ports_pos"][1], f"PORT OF LOADING: {bol_data.port_of_load}")
        c.drawString(layout["ports_pos"][0], layout["ports_pos"][1] - 15, f"PORT OF DISCHARGE: {bol_data.port_of_discharge}")
        
        # Cargo information
        c.drawString(layout["cargo_pos"][0], layout["cargo_pos"][1], f"DESCRIPTION OF GOODS:")
        c.setFont("Helvetica", 9)
        c.drawString(layout["cargo_pos"][0], layout["cargo_pos"][1] - 15, bol_data.description_of_goods)
        
        # Weight and quantity information
        c.setFont("Helvetica-Bold", 10)
        c.drawString(layout["weights_pos"][0], layout["weights_pos"][1], f"GROSS WEIGHT: {bol_data.gross_weight}")
        c.drawString(layout["weights_pos"][0], layout["weights_pos"][1] - 15, f"NET WEIGHT: {bol_data.net_weight}")
        c.drawString(layout["weights_pos"][0], layout["weights_pos"][1] - 30, f"QUANTITY: {bol_data.quantity_packages}")
        
        # Additional information
        c.drawString(layout["date_pos"][0], layout["date_pos"][1], f"FREIGHT TERMS: {bol_data.freight_terms}")
        c.drawString(layout["date_pos"][0], layout["date_pos"][1] - 15, f"DATE OF ISSUE: {bol_data.date_of_issue}")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_section(self, canvas, pos, title, name, address):
        """Helper method to draw a section with title, name, and address"""
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(pos[0], pos[1], f"{title}:")
        
        canvas.setFont("Helvetica", 9)
        y_pos = pos[1] - 15
        canvas.drawString(pos[0], y_pos, name)
        
        if address:
            for line in address.split('\\n'):
                y_pos -= 12
                canvas.drawString(pos[0], y_pos, line.strip())
    
    def _generate_simple_text_pdf(self, bol_data: SyntheticBOLData) -> bytes:
        """Fallback method when reportlab is not available"""
        # Create a simple text representation as bytes
        content = f"""
BILL OF LADING

B/L NO: {bol_data.bol_number}

SHIPPER:
{bol_data.shipper_name}
{bol_data.shipper_address.replace('\\\\n', '\\n')}

CONSIGNEE:
{bol_data.consignee_name}
{bol_data.consignee_address.replace('\\\\n', '\\n')}

NOTIFY PARTY:
{bol_data.notify_party_name}
{bol_data.notify_party_address.replace('\\\\n', '\\n')}

VESSEL: {bol_data.vessel_name}
VOYAGE: {bol_data.voyage_number}

PORT OF LOADING: {bol_data.port_of_load}
PORT OF DISCHARGE: {bol_data.port_of_discharge}

DESCRIPTION OF GOODS: {bol_data.description_of_goods}
QUANTITY: {bol_data.quantity_packages}
GROSS WEIGHT: {bol_data.gross_weight}
NET WEIGHT: {bol_data.net_weight}

FREIGHT TERMS: {bol_data.freight_terms}
DATE OF ISSUE: {bol_data.date_of_issue}
"""
        return content.encode('utf-8')
    
    def generate_test_dataset(self, count: int, output_dir: str) -> List[SyntheticBOLData]:
        """Generate a complete test dataset with ground truth"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/pdfs", exist_ok=True)
        
        dataset = []
        
        for i in range(count):
            # Generate random BOL data
            bol_data = self.generate_random_bol_data(f"TEST{i:04d}")
            
            # Randomly choose PDF type and quality
            pdf_type = random.choice(["text", "text", "text", "scanned"])  # Favor text-based
            quality = random.choice(["high", "high", "medium", "low"])     # Favor high quality
            
            bol_data.pdf_type = pdf_type
            bol_data.quality = quality
            
            # Generate PDF
            if pdf_type == "text":
                pdf_bytes = self.generate_text_based_pdf(bol_data)
            else:
                # For scanned PDFs, generate text-based first (simplified approach)
                pdf_bytes = self.generate_text_based_pdf(bol_data)
            
            # Save PDF
            pdf_path = f"{output_dir}/pdfs/{bol_data.filename}"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            dataset.append(bol_data)
        
        # Save ground truth data
        ground_truth = [asdict(bol) for bol in dataset]
        with open(f"{output_dir}/ground_truth.json", 'w') as f:
            json.dump(ground_truth, f, indent=2)
        
        return dataset
    
    def generate_edge_case_dataset(self, output_dir: str) -> List[SyntheticBOLData]:
        """Generate edge cases for testing error handling"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/pdfs", exist_ok=True)
        
        edge_cases = []
        
        # Case 1: Missing BOL number
        case1 = self.generate_random_bol_data("EDGE001")
        case1.bol_number = ""
        edge_cases.append(case1)
        
        # Case 2: Missing shipper
        case2 = self.generate_random_bol_data("EDGE002")
        case2.shipper_name = ""
        case2.shipper_address = ""
        edge_cases.append(case2)
        
        # Case 3: Missing consignee
        case3 = self.generate_random_bol_data("EDGE003")
        case3.consignee_name = ""
        case3.consignee_address = ""
        edge_cases.append(case3)
        
        # Case 4: Minimal information
        case4 = self.generate_random_bol_data("EDGE004")
        case4.vessel_name = ""
        case4.voyage_number = ""
        case4.description_of_goods = ""
        edge_cases.append(case4)
        
        # Case 5: Special characters and formatting
        case5 = self.generate_random_bol_data("EDGE005")
        case5.bol_number = "BOL/TEST-2024_001"
        case5.shipper_name = "Company & Associates (Intl.)"
        case5.gross_weight = "1,234.56 KG"
        edge_cases.append(case5)
        
        # Generate PDFs for edge cases
        for bol_data in edge_cases:
            pdf_bytes = self.generate_text_based_pdf(bol_data)
            pdf_path = f"{output_dir}/pdfs/{bol_data.filename}"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
        
        # Save ground truth
        with open(f"{output_dir}/ground_truth.json", 'w') as f:
            json.dump([asdict(bol) for bol in edge_cases], f, indent=2)
        
        return edge_cases

# Factory functions for easy test data creation
def create_test_bol_data(**kwargs) -> SyntheticBOLData:
    """Factory function to create test BOL data with defaults"""
    defaults = {
        'filename': 'test_bol.pdf',
        'bol_number': 'TEST123456',
        'shipper_name': 'Test Shipper Company',
        'shipper_address': '123 Test Street\\nTest City, TC 12345',
        'consignee_name': 'Test Consignee Corp',
        'consignee_address': '456 Test Avenue\\nTest City, TC 67890',
        'vessel_name': 'MV Test Ship',
        'voyage_number': 'VOY2024001',
        'port_of_load': 'Test Port A',
        'port_of_discharge': 'Test Port B',
        'description_of_goods': 'Test Cargo Products',
        'quantity_packages': '100 CTNS',
        'gross_weight': '5,000 KG',
        'net_weight': '4,500 KG',
        'freight_terms': 'PREPAID',
        'date_of_issue': '01/01/2024',
        'pdf_type': 'text',
        'quality': 'high',
        'layout_style': 'standard'
    }
    
    defaults.update(kwargs)
    return SyntheticBOLData(**defaults)

def create_minimal_bol_data(**kwargs) -> SyntheticBOLData:
    """Factory function to create minimal BOL data for edge case testing"""
    minimal = {
        'filename': 'minimal_bol.pdf',
        'bol_number': 'MIN001',
        'shipper_name': 'Minimal Shipper',
        'shipper_address': '',
        'consignee_name': 'Minimal Consignee',
        'consignee_address': '',
        'notify_party_name': '',
        'notify_party_address': '',
        'vessel_name': '',
        'voyage_number': '',
        'port_of_load': '',
        'port_of_discharge': '',
        'description_of_goods': '',
        'quantity_packages': '',
        'gross_weight': '',
        'net_weight': '',
        'freight_terms': '',
        'date_of_issue': '',
        'pdf_type': 'text',
        'quality': 'low',
        'layout_style': 'standard'
    }
    
    minimal.update(kwargs)
    return SyntheticBOLData(**minimal)

# Command line usage
if __name__ == "__main__":
    generator = SyntheticBOLGenerator()
    
    # Generate test datasets
    print("Generating synthetic BOL test datasets...")
    
    # Small dataset for quick testing
    small_dataset = generator.generate_test_dataset(20, "tests/fixtures/small_dataset")
    print(f"Generated {len(small_dataset)} BOL PDFs for small dataset")
    
    # Performance dataset
    perf_dataset = generator.generate_test_dataset(100, "tests/fixtures/performance_dataset")
    print(f"Generated {len(perf_dataset)} BOL PDFs for performance testing")
    
    # Edge cases
    edge_cases = generator.generate_edge_case_dataset("tests/fixtures/edge_cases")
    print(f"Generated {len(edge_cases)} edge case BOL PDFs")
    
    print("Synthetic test data generation completed!")