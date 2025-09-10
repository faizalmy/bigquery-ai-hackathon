"""
Legal Document Data Ingestion
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module handles the acquisition and loading of legal document datasets
for the BigQuery AI implementation.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalDataIngestion:
    """Handles legal document data acquisition and ingestion."""

    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize the data ingestion system.

        Args:
            data_dir: Directory to store raw data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Legal document sources
        self.data_sources = {
            'sample_legal_docs': {
                'name': 'Sample Legal Documents',
                'description': 'Curated sample legal documents for testing',
                'url': None,  # Will be created locally
                'expected_count': 500
            }
        }

    def create_sample_legal_documents(self) -> List[Dict[str, Any]]:
        """
        Create sample legal documents for testing BigQuery AI functions.

        Returns:
            List of sample legal documents
        """
        logger.info("Creating sample legal documents for testing")

        sample_documents = [
            {
                "document_id": "doc_001",
                "document_type": "contract",
                "title": "Software License Agreement",
                "content": """
                SOFTWARE LICENSE AGREEMENT

                This Software License Agreement ("Agreement") is entered into on January 15, 2024,
                between TechCorp Inc. ("Licensor") and ClientCorp LLC ("Licensee").

                TERMS AND CONDITIONS:
                1. Grant of License: Licensor hereby grants to Licensee a non-exclusive,
                   non-transferable license to use the Software.
                2. Restrictions: Licensee shall not reverse engineer, decompile, or disassemble the Software.
                3. Term: This Agreement shall remain in effect for a period of two (2) years.
                4. Termination: Either party may terminate this Agreement with thirty (30) days written notice.
                5. Governing Law: This Agreement shall be governed by the laws of the State of California.

                IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.
                """,
                "metadata": {
                    "parties": ["TechCorp Inc.", "ClientCorp LLC"],
                    "document_type": "contract",
                    "jurisdiction": "California",
                    "date": "2024-01-15",
                    "urgency": "standard"
                }
            },
            {
                "document_id": "doc_002",
                "document_type": "case_file",
                "title": "Supreme Court Case: Smith v. Jones",
                "content": """
                SUPREME COURT OF THE UNITED STATES

                SMITH v. JONES
                No. 23-1234

                Argued January 10, 2024 — Decided March 15, 2024

                Petitioner John Smith filed a petition for writ of certiorari challenging
                the decision of the Court of Appeals for the Ninth Circuit. The case
                involves a constitutional question regarding the First Amendment right
                to free speech in the context of social media platforms.

                ISSUES PRESENTED:
                1. Whether social media platforms are subject to First Amendment constraints
                2. Whether the government can regulate content moderation policies
                3. Whether the Communications Decency Act Section 230 provides immunity

                HOLDING: The Court held that social media platforms are not state actors
                and therefore not subject to First Amendment constraints. The government
                cannot compel platforms to host content they find objectionable.

                DECISION: Affirmed in part, reversed in part. The judgment of the Court
                of Appeals is affirmed with respect to the First Amendment claim but
                reversed regarding the Section 230 immunity question.
                """,
                "metadata": {
                    "parties": ["John Smith", "Jones Corporation"],
                    "document_type": "case_file",
                    "court": "Supreme Court",
                    "date": "2024-03-15",
                    "urgency": "high",
                    "legal_issues": ["First Amendment", "Section 230", "Social Media"]
                }
            },
            {
                "document_id": "doc_003",
                "document_type": "legal_brief",
                "title": "Motion for Summary Judgment",
                "content": """
                IN THE UNITED STATES DISTRICT COURT
                FOR THE NORTHERN DISTRICT OF CALIFORNIA

                ABC CORPORATION, Plaintiff,
                v.
                XYZ ENTERPRISES, Defendant.

                Case No. 3:24-cv-00123

                PLAINTIFF'S MOTION FOR SUMMARY JUDGMENT

                TO THE HONORABLE COURT:

                Plaintiff ABC Corporation respectfully moves this Court for summary judgment
                pursuant to Federal Rule of Civil Procedure 56 on all claims asserted in
                the Complaint.

                STATEMENT OF UNDISPUTED FACTS:
                1. On January 1, 2024, Defendant XYZ Enterprises entered into a contract
                   with Plaintiff ABC Corporation.
                2. The contract required Defendant to deliver 1,000 units of Product X
                   by March 1, 2024.
                3. Defendant failed to deliver the required units by the specified date.
                4. Plaintiff has suffered damages in the amount of $500,000 as a result
                   of Defendant's breach.

                LEGAL ARGUMENT:
                Summary judgment is appropriate when there is no genuine dispute as to
                any material fact and the moving party is entitled to judgment as a matter
                of law. Fed. R. Civ. P. 56(a). Here, the undisputed facts establish that
                Defendant materially breached the contract, entitling Plaintiff to damages.

                CONCLUSION:
                For the foregoing reasons, Plaintiff respectfully requests that this Court
                grant summary judgment in favor of Plaintiff on all claims.
                """,
                "metadata": {
                    "parties": ["ABC Corporation", "XYZ Enterprises"],
                    "document_type": "legal_brief",
                    "court": "District Court",
                    "date": "2024-04-01",
                    "urgency": "high",
                    "legal_issues": ["Breach of Contract", "Summary Judgment", "Damages"]
                }
            },
            {
                "document_id": "doc_004",
                "document_type": "statute",
                "title": "California Consumer Privacy Act",
                "content": """
                CALIFORNIA CONSUMER PRIVACY ACT
                Civil Code Section 1798.100 et seq.

                SECTION 1798.100. RIGHT TO KNOW ABOUT PERSONAL INFORMATION COLLECTED

                (a) A consumer shall have the right to request that a business that
                collects personal information about the consumer disclose to the consumer
                the following:

                (1) The categories of personal information it has collected about that consumer.
                (2) The categories of sources from which the personal information is collected.
                (3) The business or commercial purpose for collecting or selling personal information.
                (4) The categories of third parties with whom the business shares personal information.
                (5) The specific pieces of personal information it has collected about that consumer.

                (b) A business that receives a verifiable consumer request from a consumer
                to know personal information shall promptly take steps to disclose and deliver,
                free of charge to the consumer, the personal information required by this section.

                SECTION 1798.105. RIGHT TO DELETE PERSONAL INFORMATION

                (a) A consumer shall have the right to request that a business delete
                any personal information about the consumer which the business has collected
                from the consumer.

                (b) A business that receives a verifiable consumer request from a consumer
                to delete the consumer's personal information shall delete the consumer's
                personal information from its records and direct any service providers
                to delete the consumer's personal information from their records.
                """,
                "metadata": {
                    "document_type": "statute",
                    "jurisdiction": "California",
                    "date": "2020-01-01",
                    "urgency": "standard",
                    "legal_issues": ["Privacy", "Consumer Rights", "Data Protection"]
                }
            },
            {
                "document_id": "doc_005",
                "document_type": "case_file",
                "title": "Employment Discrimination Case",
                "content": """
                IN THE UNITED STATES DISTRICT COURT
                FOR THE EASTERN DISTRICT OF NEW YORK

                JANE DOE, Plaintiff,
                v.
                MEGACORP INC., Defendant.

                Case No. 2:24-cv-00567

                COMPLAINT FOR EMPLOYMENT DISCRIMINATION

                Plaintiff Jane Doe, by and through her attorneys, alleges as follows:

                JURISDICTION AND VENUE:
                1. This Court has jurisdiction pursuant to 28 U.S.C. § 1331 and 42 U.S.C. § 2000e-5(f).
                2. Venue is proper in this district pursuant to 28 U.S.C. § 1391.

                PARTIES:
                3. Plaintiff Jane Doe is a resident of New York and was employed by Defendant.
                4. Defendant Megacorp Inc. is a corporation doing business in New York.

                FACTS:
                5. Plaintiff was employed by Defendant from January 2020 to December 2023.
                6. Throughout her employment, Plaintiff performed her duties satisfactorily
                   and received positive performance reviews.
                7. In March 2023, Plaintiff informed Defendant that she was pregnant.
                8. Following her pregnancy announcement, Defendant began treating Plaintiff
                   differently, including:
                   a. Excluding her from important meetings
                   b. Reducing her responsibilities
                   c. Making negative comments about her pregnancy
                9. On December 15, 2023, Defendant terminated Plaintiff's employment,
                   citing "performance issues" that were not previously documented.

                CAUSES OF ACTION:
                COUNT I: PREGNANCY DISCRIMINATION
                10. Defendant's actions constitute unlawful pregnancy discrimination
                    in violation of Title VII of the Civil Rights Act of 1964.

                COUNT II: RETALIATION
                11. Defendant's termination of Plaintiff was in retaliation for her
                    pregnancy and constitutes unlawful retaliation under Title VII.

                PRAYER FOR RELIEF:
                WHEREFORE, Plaintiff respectfully requests that this Court:
                A. Award Plaintiff back pay and front pay
                B. Award Plaintiff compensatory and punitive damages
                C. Grant such other relief as the Court deems just and proper.
                """,
                "metadata": {
                    "parties": ["Jane Doe", "Megacorp Inc."],
                    "document_type": "case_file",
                    "court": "District Court",
                    "date": "2024-01-15",
                    "urgency": "high",
                    "legal_issues": ["Employment Discrimination", "Pregnancy Discrimination", "Title VII"]
                }
            }
        ]

        # Generate additional sample documents to reach target count
        additional_docs = self._generate_additional_documents(495)  # 500 total - 5 existing
        sample_documents.extend(additional_docs)

        logger.info(f"Created {len(sample_documents)} sample legal documents")
        return sample_documents

    def _generate_additional_documents(self, count: int) -> List[Dict[str, Any]]:
        """Generate additional sample documents to reach target count."""
        additional_docs = []

        document_templates = [
            {
                "type": "contract",
                "titles": ["Service Agreement", "Employment Contract", "NDA", "Purchase Agreement"],
                "content_template": "This {type} is entered into between {party1} and {party2} on {date}. Terms include {terms}."
            },
            {
                "type": "case_file",
                "titles": ["Personal Injury Case", "Contract Dispute", "Property Case", "Family Law Case"],
                "content_template": "In the matter of {case_name}, the court finds that {finding}. The parties are {parties}."
            },
            {
                "type": "legal_brief",
                "titles": ["Motion to Dismiss", "Motion for Injunction", "Appeal Brief", "Response Brief"],
                "content_template": "This {type} requests that the court {request}. The legal basis is {basis}."
            }
        ]

        for i in range(count):
            template = document_templates[i % len(document_templates)]
            doc_id = f"doc_{i+6:03d}"

            doc = {
                "document_id": doc_id,
                "document_type": template["type"],
                "title": f"{template['titles'][i % len(template['titles'])]} {i+1}",
                "content": template["content_template"].format(
                    type=template["type"],
                    party1="Party A",
                    party2="Party B",
                    date="2024-01-01",
                    terms="standard terms and conditions",
                    case_name=f"Case {i+1}",
                    finding="the plaintiff has established a prima facie case",
                    parties="bound by the terms of this agreement",
                    request="grant the requested relief",
                    basis="established legal precedent"
                ),
                "metadata": {
                    "document_type": template["type"],
                    "date": "2024-01-01",
                    "urgency": "standard" if i % 3 == 0 else "medium" if i % 3 == 1 else "high"
                }
            }
            additional_docs.append(doc)

        return additional_docs

    def load_legal_datasets(self) -> Dict[str, Any]:
        """
        Load existing legal datasets for MVP.

        Returns:
            Dictionary containing loaded datasets
        """
        logger.info("Loading legal datasets for MVP")

        # Create sample documents
        sample_docs = self.create_sample_legal_documents()

        # Save to file
        output_file = self.data_dir / "sample_legal_documents.json"
        with open(output_file, 'w') as f:
            json.dump(sample_docs, f, indent=2)

        logger.info(f"Saved {len(sample_docs)} documents to {output_file}")

        return {
            'sample_legal_docs': {
                'documents': sample_docs,
                'count': len(sample_docs),
                'file_path': str(output_file),
                'loaded_at': datetime.now().isoformat()
            }
        }

    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about available datasets.

        Returns:
            Dataset information dictionary
        """
        return {
            'available_datasets': list(self.data_sources.keys()),
            'data_sources': self.data_sources,
            'data_directory': str(self.data_dir),
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Test the legal data ingestion system."""
    print("📊 Legal Document Data Ingestion - Phase 2.1")
    print("=" * 60)

    # Initialize ingestion system
    ingestion = LegalDataIngestion()

    # Load datasets
    datasets = ingestion.load_legal_datasets()

    # Print summary
    for name, data in datasets.items():
        print(f"✅ {name}: {data['count']} documents loaded")

    print(f"\n📁 Data saved to: {ingestion.data_dir}")
    print("✅ Legal data ingestion completed successfully")

if __name__ == "__main__":
    main()
