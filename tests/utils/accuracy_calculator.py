"""
Accuracy calculation and quality metrics for BOL OCR extraction testing
"""

from typing import List, Dict, Tuple, Optional
import json
import re
from dataclasses import asdict
from difflib import SequenceMatcher
import statistics

# Import app classes for type hints
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app import BOLData
from tests.utils.synthetic_data_generator import SyntheticBOLData

class AccuracyCalculator:
    """Calculate extraction accuracy metrics against ground truth data"""
    
    def __init__(self):
        # Field importance weights for overall accuracy calculation
        self.field_weights = {
            'bol_number': 1.0,          # Critical - must be accurate
            'shipper_name': 0.9,        # Very important for shipping
            'consignee_name': 0.9,      # Very important for delivery
            'vessel_name': 0.8,         # Important for tracking
            'port_of_load': 0.8,        # Important for logistics
            'port_of_discharge': 0.8,   # Important for logistics
            'gross_weight': 0.7,        # Moderately important
            'quantity_packages': 0.7,   # Moderately important
            'freight_terms': 0.6,       # Useful for billing
            'date_of_issue': 0.6,       # Useful for tracking
            'voyage_number': 0.5,       # Nice to have
            'notify_party_name': 0.5,   # Nice to have
            'description_of_goods': 0.4 # Often varies in format
        }
        
        # Success thresholds for different metrics
        self.success_thresholds = {
            'excellent': 0.95,
            'good': 0.85,
            'acceptable': 0.70,
            'poor': 0.50
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Remove common punctuation that doesn't affect meaning
        normalized = re.sub(r'[.,;:\-_(){}[\]"]', ' ', normalized)
        
        # Remove extra spaces again
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def calculate_string_similarity(self, str1: str, str2: str, method: str = "sequence") -> float:
        """Calculate similarity between two strings using different methods"""
        if not str1 and not str2:
            return 1.0  # Both empty
        
        if not str1 or not str2:
            return 0.0  # One empty, one not
        
        # Normalize strings
        norm_str1 = self.normalize_text(str1)
        norm_str2 = self.normalize_text(str2)
        
        if norm_str1 == norm_str2:
            return 1.0  # Exact match after normalization
        
        if method == "sequence":
            # Use SequenceMatcher for fuzzy matching
            return SequenceMatcher(None, norm_str1, norm_str2).ratio()
        
        elif method == "jaccard":
            # Jaccard similarity using word sets
            words1 = set(norm_str1.split())
            words2 = set(norm_str2.split())
            
            if not words1 and not words2:
                return 1.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
        
        elif method == "character_overlap":
            # Character-level overlap
            chars1 = set(norm_str1.replace(' ', ''))
            chars2 = set(norm_str2.replace(' ', ''))
            
            if not chars1 and not chars2:
                return 1.0
            
            intersection = chars1.intersection(chars2)
            union = chars1.union(chars2)
            
            return len(intersection) / len(union) if union else 0.0
        
        else:
            raise ValueError(f"Unknown similarity method: {method}")
    
    def calculate_field_accuracy(self, extracted: str, expected: str, 
                                field_type: str = "general") -> Dict[str, float]:
        """Calculate accuracy for a single field using multiple methods"""
        results = {}
        
        # Exact match
        results['exact_match'] = 1.0 if extracted == expected else 0.0
        
        # Normalized exact match
        results['normalized_exact'] = 1.0 if self.normalize_text(extracted) == self.normalize_text(expected) else 0.0
        
        # Fuzzy matching scores
        results['sequence_similarity'] = self.calculate_string_similarity(extracted, expected, "sequence")
        results['jaccard_similarity'] = self.calculate_string_similarity(extracted, expected, "jaccard")
        results['character_overlap'] = self.calculate_string_similarity(extracted, expected, "character_overlap")
        
        # Field-specific accuracy adjustments
        if field_type == "bol_number":
            # BOL numbers should be exact matches
            results['field_accuracy'] = results['normalized_exact']
        elif field_type in ["weight", "quantity"]:
            # Numeric fields - extract numbers and compare
            results['field_accuracy'] = self._calculate_numeric_accuracy(extracted, expected)
        elif field_type in ["shipper_name", "consignee_name", "vessel_name"]:
            # Names - use sequence similarity with high threshold
            results['field_accuracy'] = results['sequence_similarity']
        else:
            # General fields - use average of similarity methods
            similarity_scores = [results['sequence_similarity'], results['jaccard_similarity']]
            results['field_accuracy'] = sum(similarity_scores) / len(similarity_scores)
        
        return results
    
    def _calculate_numeric_accuracy(self, extracted: str, expected: str) -> float:
        """Calculate accuracy for numeric fields (weights, quantities)"""
        # Extract numbers from both strings
        extracted_nums = re.findall(r'[\d,]+\.?\d*', extracted.replace(',', ''))
        expected_nums = re.findall(r'[\d,]+\.?\d*', expected.replace(',', ''))
        
        if not expected_nums:
            return 1.0 if not extracted_nums else 0.0
        
        if not extracted_nums:
            return 0.0
        
        try:
            # Compare the first (primary) number found
            extracted_val = float(extracted_nums[0])
            expected_val = float(expected_nums[0])
            
            if expected_val == 0:
                return 1.0 if extracted_val == 0 else 0.0
            
            # Calculate percentage difference
            percentage_diff = abs(extracted_val - expected_val) / expected_val
            
            # High accuracy if within 5%, good if within 10%, poor if within 25%
            if percentage_diff <= 0.05:
                return 1.0
            elif percentage_diff <= 0.10:
                return 0.8
            elif percentage_diff <= 0.25:
                return 0.5
            else:
                return 0.0
                
        except (ValueError, IndexError):
            # Fall back to string similarity if numeric conversion fails
            return self.calculate_string_similarity(extracted, expected, "sequence")
    
    def calculate_bol_accuracy(self, extracted: BOLData, expected: SyntheticBOLData) -> Dict[str, any]:
        """Calculate comprehensive accuracy metrics for a single BOL"""
        results = {
            'filename': extracted.filename,
            'field_accuracies': {},
            'field_scores': {},
            'extraction_metadata': {
                'method': extracted.extraction_method,
                'confidence': extracted.extraction_confidence,
                'failed': extracted.extraction_failed
            }
        }
        
        # Field mapping between extracted and expected data
        field_mapping = {
            'bol_number': (extracted.bol_number, expected.bol_number, 'bol_number'),
            'shipper_name': (extracted.shipper_name, expected.shipper_name, 'shipper_name'),
            'consignee_name': (extracted.consignee_name, expected.consignee_name, 'consignee_name'),
            'vessel_name': (extracted.vessel_name, expected.vessel_name, 'vessel_name'),
            'voyage_number': (extracted.voyage_number, expected.voyage_number, 'general'),
            'port_of_load': (extracted.port_of_load, expected.port_of_load, 'general'),
            'port_of_discharge': (extracted.port_of_discharge, expected.port_of_discharge, 'general'),
            'gross_weight': (extracted.gross_weight, expected.gross_weight, 'weight'),
            'quantity_packages': (extracted.quantity_packages, expected.quantity_packages, 'quantity'),
            'freight_terms': (extracted.freight_terms, expected.freight_terms, 'general'),
            'date_of_issue': (extracted.date_of_issue, expected.date_of_issue, 'general'),
            'description_of_goods': (extracted.description_of_goods, expected.description_of_goods, 'general')
        }
        
        # Calculate accuracy for each field
        for field_name, (ext_val, exp_val, field_type) in field_mapping.items():
            field_accuracy = self.calculate_field_accuracy(ext_val or "", exp_val or "", field_type)
            results['field_accuracies'][field_name] = field_accuracy
            results['field_scores'][field_name] = field_accuracy['field_accuracy']
        
        # Calculate weighted overall accuracy
        weighted_sum = 0
        total_weight = 0
        
        for field_name, score in results['field_scores'].items():
            weight = self.field_weights.get(field_name, 0.3)
            weighted_sum += score * weight
            total_weight += weight
        
        results['overall_accuracy'] = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Calculate category-specific accuracies
        results['category_accuracies'] = self._calculate_category_accuracies(results['field_scores'])
        
        return results
    
    def _calculate_category_accuracies(self, field_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate accuracy for different categories of fields"""
        categories = {
            'critical_fields': ['bol_number', 'shipper_name', 'consignee_name'],
            'logistics_fields': ['vessel_name', 'port_of_load', 'port_of_discharge'],
            'cargo_fields': ['description_of_goods', 'gross_weight', 'quantity_packages'],
            'administrative_fields': ['freight_terms', 'date_of_issue', 'voyage_number']
        }
        
        category_accuracies = {}
        
        for category, fields in categories.items():
            scores = [field_scores.get(field, 0.0) for field in fields if field in field_scores]
            category_accuracies[category] = statistics.mean(scores) if scores else 0.0
        
        return category_accuracies
    
    def calculate_dataset_accuracy(self, extracted_results: List[BOLData], 
                                 ground_truth: List[SyntheticBOLData]) -> Dict[str, any]:
        """Calculate comprehensive accuracy metrics for entire dataset"""
        if len(extracted_results) != len(ground_truth):
            raise ValueError(f"Dataset size mismatch: {len(extracted_results)} vs {len(ground_truth)}")
        
        # Calculate individual BOL accuracies
        individual_results = []
        for extracted, expected in zip(extracted_results, ground_truth):
            bol_accuracy = self.calculate_bol_accuracy(extracted, expected)
            individual_results.append(bol_accuracy)
        
        # Aggregate statistics
        dataset_summary = self._calculate_dataset_summary(individual_results)
        
        # Performance by extraction method
        method_performance = self._calculate_method_performance(individual_results)
        
        # Quality distribution
        quality_distribution = self._calculate_quality_distribution(individual_results)
        
        return {
            'dataset_size': len(extracted_results),
            'individual_results': individual_results,
            'summary_statistics': dataset_summary,
            'method_performance': method_performance,
            'quality_distribution': quality_distribution,
            'success_rates': self._calculate_success_rates(individual_results)
        }
    
    def _calculate_dataset_summary(self, individual_results: List[Dict]) -> Dict[str, any]:
        """Calculate summary statistics for the dataset"""
        # Extract overall accuracies
        overall_accuracies = [result['overall_accuracy'] for result in individual_results]
        
        # Extract field accuracies
        field_accuracies = {}
        for field in self.field_weights.keys():
            field_scores = [result['field_scores'].get(field, 0.0) for result in individual_results]
            field_accuracies[field] = {
                'mean': statistics.mean(field_scores),
                'median': statistics.median(field_scores),
                'std_dev': statistics.stdev(field_scores) if len(field_scores) > 1 else 0.0,
                'min': min(field_scores),
                'max': max(field_scores),
                'above_70_percent': sum(1 for score in field_scores if score >= 0.7) / len(field_scores),
                'above_85_percent': sum(1 for score in field_scores if score >= 0.85) / len(field_scores),
                'above_95_percent': sum(1 for score in field_scores if score >= 0.95) / len(field_scores)
            }
        
        # Category accuracies
        category_accuracies = {}
        categories = ['critical_fields', 'logistics_fields', 'cargo_fields', 'administrative_fields']
        
        for category in categories:
            category_scores = [result['category_accuracies'].get(category, 0.0) for result in individual_results]
            category_accuracies[category] = {
                'mean': statistics.mean(category_scores),
                'median': statistics.median(category_scores),
                'std_dev': statistics.stdev(category_scores) if len(category_scores) > 1 else 0.0
            }
        
        return {
            'overall_accuracy': {
                'mean': statistics.mean(overall_accuracies),
                'median': statistics.median(overall_accuracies),
                'std_dev': statistics.stdev(overall_accuracies) if len(overall_accuracies) > 1 else 0.0,
                'min': min(overall_accuracies),
                'max': max(overall_accuracies)
            },
            'field_accuracies': field_accuracies,
            'category_accuracies': category_accuracies
        }
    
    def _calculate_method_performance(self, individual_results: List[Dict]) -> Dict[str, Dict]:
        """Calculate performance statistics by extraction method"""
        methods = {}
        
        for result in individual_results:
            method = result['extraction_metadata']['method']
            if method not in methods:
                methods[method] = []
            methods[method].append(result['overall_accuracy'])
        
        method_stats = {}
        for method, accuracies in methods.items():
            if accuracies:
                method_stats[method] = {
                    'count': len(accuracies),
                    'mean_accuracy': statistics.mean(accuracies),
                    'median_accuracy': statistics.median(accuracies),
                    'std_dev': statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0,
                    'success_rate_70': sum(1 for acc in accuracies if acc >= 0.7) / len(accuracies),
                    'success_rate_85': sum(1 for acc in accuracies if acc >= 0.85) / len(accuracies)
                }
        
        return method_stats
    
    def _calculate_quality_distribution(self, individual_results: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of results by quality levels"""
        distribution = {
            'excellent': 0,  # >= 95%
            'good': 0,       # >= 85%
            'acceptable': 0,  # >= 70%
            'poor': 0,       # >= 50%
            'failed': 0      # < 50%
        }
        
        for result in individual_results:
            accuracy = result['overall_accuracy']
            
            if accuracy >= self.success_thresholds['excellent']:
                distribution['excellent'] += 1
            elif accuracy >= self.success_thresholds['good']:
                distribution['good'] += 1
            elif accuracy >= self.success_thresholds['acceptable']:
                distribution['acceptable'] += 1
            elif accuracy >= self.success_thresholds['poor']:
                distribution['poor'] += 1
            else:
                distribution['failed'] += 1
        
        return distribution
    
    def _calculate_success_rates(self, individual_results: List[Dict]) -> Dict[str, float]:
        """Calculate various success rate metrics"""
        total_count = len(individual_results)
        
        if total_count == 0:
            return {}
        
        # Overall success rates
        accuracies = [result['overall_accuracy'] for result in individual_results]
        
        success_rates = {}
        for threshold_name, threshold_value in self.success_thresholds.items():
            success_count = sum(1 for acc in accuracies if acc >= threshold_value)
            success_rates[f'success_rate_{threshold_name}'] = success_count / total_count
        
        # Extraction failure rate
        failed_extractions = sum(1 for result in individual_results 
                               if result['extraction_metadata']['failed'])
        success_rates['extraction_failure_rate'] = failed_extractions / total_count
        
        return success_rates
    
    def generate_accuracy_report(self, dataset_results: Dict[str, any], 
                               output_file: Optional[str] = None) -> str:
        """Generate a comprehensive accuracy report"""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("BOL OCR EXTRACTION ACCURACY REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Dataset Size: {dataset_results['dataset_size']} BOL documents")
        report_lines.append("")
        
        # Overall Performance Summary
        overall = dataset_results['summary_statistics']['overall_accuracy']
        report_lines.append("OVERALL PERFORMANCE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Mean Accuracy: {overall['mean']:.1%}")
        report_lines.append(f"Median Accuracy: {overall['median']:.1%}")
        report_lines.append(f"Standard Deviation: {overall['std_dev']:.1%}")
        report_lines.append(f"Range: {overall['min']:.1%} - {overall['max']:.1%}")
        report_lines.append("")
        
        # Success Rates
        success_rates = dataset_results['success_rates']
        report_lines.append("SUCCESS RATES")
        report_lines.append("-" * 40)
        for rate_name, rate_value in success_rates.items():
            if 'success_rate' in rate_name:
                threshold_name = rate_name.replace('success_rate_', '').title()
                report_lines.append(f"{threshold_name} (≥{self.success_thresholds.get(rate_name.replace('success_rate_', ''), 0.5):.0%}): {rate_value:.1%}")
        report_lines.append(f"Extraction Failures: {success_rates.get('extraction_failure_rate', 0):.1%}")
        report_lines.append("")
        
        # Field-by-Field Performance
        field_accuracies = dataset_results['summary_statistics']['field_accuracies']
        report_lines.append("FIELD-BY-FIELD PERFORMANCE")
        report_lines.append("-" * 40)
        
        # Sort fields by importance (weight)
        sorted_fields = sorted(field_accuracies.items(), 
                             key=lambda x: self.field_weights.get(x[0], 0), 
                             reverse=True)
        
        for field_name, stats in sorted_fields:
            weight = self.field_weights.get(field_name, 0.3)
            report_lines.append(f"{field_name.replace('_', ' ').title():<25} "
                              f"Mean: {stats['mean']:.1%} "
                              f"≥85%: {stats['above_85_percent']:.1%} "
                              f"Weight: {weight:.1f}")
        report_lines.append("")
        
        # Method Performance Comparison
        method_perf = dataset_results['method_performance']
        if len(method_perf) > 1:
            report_lines.append("EXTRACTION METHOD COMPARISON")
            report_lines.append("-" * 40)
            for method, stats in method_perf.items():
                report_lines.append(f"{method.upper():<10} "
                                  f"Count: {stats['count']:<4} "
                                  f"Mean: {stats['mean_accuracy']:.1%} "
                                  f"≥85%: {stats['success_rate_85']:.1%}")
            report_lines.append("")
        
        # Quality Distribution
        quality_dist = dataset_results['quality_distribution']
        report_lines.append("QUALITY DISTRIBUTION")
        report_lines.append("-" * 40)
        total = sum(quality_dist.values())
        for quality, count in quality_dist.items():
            percentage = count / total if total > 0 else 0
            report_lines.append(f"{quality.title():<12} {count:<4} ({percentage:.1%})")
        report_lines.append("")
        
        # Category Performance
        category_accuracies = dataset_results['summary_statistics']['category_accuracies']
        report_lines.append("CATEGORY PERFORMANCE")
        report_lines.append("-" * 40)
        for category, stats in category_accuracies.items():
            category_name = category.replace('_', ' ').title()
            report_lines.append(f"{category_name:<20} Mean: {stats['mean']:.1%}")
        
        # Join all lines
        report_text = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text

# Success criteria definitions for automated testing
SUCCESS_CRITERIA = {
    'field_accuracy_targets': {
        'bol_number': 0.95,        # 95% accuracy target - critical field
        'shipper_name': 0.85,      # 85% accuracy target - very important
        'consignee_name': 0.85,    # 85% accuracy target - very important  
        'vessel_name': 0.80,       # 80% accuracy target - important
        'port_of_load': 0.80,      # 80% accuracy target - important
        'port_of_discharge': 0.80, # 80% accuracy target - important
        'gross_weight': 0.75,      # 75% accuracy target - moderately important
        'quantity_packages': 0.75, # 75% accuracy target - moderately important
        'overall_accuracy': 0.80   # 80% overall accuracy target
    },
    'success_rate_targets': {
        'acceptable_rate': 0.90,   # 90% of documents should be ≥70% accurate
        'good_rate': 0.70,         # 70% of documents should be ≥85% accurate
        'excellent_rate': 0.40,    # 40% of documents should be ≥95% accurate
        'failure_rate': 0.05       # <5% extraction failure rate
    },
    'method_performance_targets': {
        'text_method_accuracy': 0.85,  # Text extraction should average ≥85%
        'ocr_method_accuracy': 0.70,   # OCR extraction should average ≥70%
        'confidence_correlation': 0.6  # Confidence should correlate with accuracy
    }
}

def evaluate_against_criteria(dataset_results: Dict[str, any]) -> Dict[str, bool]:
    """Evaluate dataset results against success criteria"""
    evaluation = {}
    
    # Field accuracy targets
    field_accuracies = dataset_results['summary_statistics']['field_accuracies']
    for field, target in SUCCESS_CRITERIA['field_accuracy_targets'].items():
        if field in field_accuracies:
            actual = field_accuracies[field]['mean']
            evaluation[f'field_{field}_target'] = actual >= target
        elif field == 'overall_accuracy':
            actual = dataset_results['summary_statistics']['overall_accuracy']['mean']
            evaluation[f'field_{field}_target'] = actual >= target
    
    # Success rate targets
    success_rates = dataset_results['success_rates']
    targets = SUCCESS_CRITERIA['success_rate_targets']
    
    evaluation['acceptable_rate_target'] = success_rates.get('success_rate_acceptable', 0) >= targets['acceptable_rate']
    evaluation['good_rate_target'] = success_rates.get('success_rate_good', 0) >= targets['good_rate']
    evaluation['excellent_rate_target'] = success_rates.get('success_rate_excellent', 0) >= targets['excellent_rate']
    evaluation['failure_rate_target'] = success_rates.get('extraction_failure_rate', 1) <= targets['failure_rate']
    
    # Method performance targets
    method_perf = dataset_results['method_performance']
    method_targets = SUCCESS_CRITERIA['method_performance_targets']
    
    if 'text' in method_perf:
        evaluation['text_method_target'] = method_perf['text']['mean_accuracy'] >= method_targets['text_method_accuracy']
    
    if 'ocr' in method_perf:
        evaluation['ocr_method_target'] = method_perf['ocr']['mean_accuracy'] >= method_targets['ocr_method_accuracy']
    
    # Overall evaluation
    evaluation['overall_success'] = all(evaluation.values())
    
    return evaluation