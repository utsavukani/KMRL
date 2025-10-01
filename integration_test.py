#!/usr/bin/env python3
"""
KMRL System Integration Test Suite
SIH25081 - Comprehensive testing for train optimization system

This test suite validates:
- Backend API endpoints functionality
- Optimization algorithm performance
- Data validation and processing
- ML prediction accuracy
- Frontend-backend integration
- Error handling and edge cases
"""

import asyncio
import aiohttp
import pandas as pd
import json
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import os

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KMRLIntegrationTester:
    """
    Comprehensive integration test suite for KMRL optimization system
    Tests all components from data ingestion to frontend display
    """

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_results = {}
        self.session = None

    async def run_full_test_suite(self):
        """Run complete integration test suite"""

        print("🚄 KMRL System Integration Test Suite")
        print("=" * 60)
        print(f"Testing system at: {self.base_url}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        async with aiohttp.ClientSession() as session:
            self.session = session

            # Test categories
            test_categories = [
                ("System Health Check", self.test_system_health),
                ("Data Validation", self.test_data_validation),
                ("Synthetic Data Generation", self.test_synthetic_data),
                ("ML Prediction Engine", self.test_ml_predictions),
                ("Optimization Algorithm", self.test_optimization_engine),
                ("API Endpoints", self.test_api_endpoints),
                ("What-If Simulation", self.test_what_if_simulation),
                ("Performance & Load", self.test_performance),
                ("Error Handling", self.test_error_handling),
                ("Frontend Integration", self.test_frontend_integration)
            ]

            overall_success = True

            for category_name, test_function in test_categories:
                print(f"🧪 Testing: {category_name}")
                try:
                    result = await test_function()
                    self.test_results[category_name] = result

                    if result['success']:
                        print(
                            f"✅ {category_name}: PASSED ({result['tests_passed']}/{result['total_tests']} tests)")
                    else:
                        print(
                            f"❌ {category_name}: FAILED ({result['tests_passed']}/{result['total_tests']} tests)")
                        overall_success = False

                    if result.get('warnings'):
                        print(f"⚠️  Warnings: {len(result['warnings'])}")

                except Exception as e:
                    print(f"💥 {category_name}: ERROR - {str(e)}")
                    self.test_results[category_name] = {
                        'success': False, 'error': str(e), 'total_tests': 1, 'tests_passed': 0
                    }
                    overall_success = False

                print()

        # Generate test report
        self.generate_test_report(overall_success)
        return overall_success

    async def test_system_health(self) -> Dict[str, Any]:
        """Test system health and component availability"""

        tests = []

        # Test 1: Health endpoint
        try:
            async with self.session.get(f"{self.api_base}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    tests.append(("Health endpoint accessible", True))

                    # Check components
                    if 'database' in health_data:
                        tests.append(
                            ("Database connection", health_data['database'] == 'healthy'))
                    if 'ml_models' in health_data:
                        tests.append(
                            ("ML models loaded", health_data['ml_models'] == 'ready'))
                else:
                    tests.append(("Health endpoint accessible", False))
        except Exception as e:
            tests.append(("Health endpoint accessible", False))

        # Test 2: Backend server running
        try:
            async with self.session.get(self.base_url) as response:
                tests.append(("Backend server responding",
                             response.status in [200, 404]))
        except:
            tests.append(("Backend server responding", False))

        # Test 3: Required directories exist
        required_dirs = ['data', 'backend', 'frontend', 'deployment']
        for directory in required_dirs:
            tests.append(
                (f"Directory '{directory}' exists", os.path.exists(directory)))

        # Test 4: Required files exist
        critical_files = [
            'backend/main.py',
            'backend/models/cp_sat_solver.py',
            'backend/models/genetic_optimizer.py',
            'backend/models/ml_predictor.py',
            'frontend/index.html',
            'data/generate_synthetic_data.py'
        ]

        for file_path in critical_files:
            tests.append((f"File '{file_path}' exists",
                         os.path.exists(file_path)))

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests
        }

    async def test_data_validation(self) -> Dict[str, Any]:
        """Test data validation and cleaning functionality"""

        tests = []
        warnings = []

        try:
            # Import validation module
            sys.path.append('backend/utils')
            from data_validation import DataValidator

            validator = DataValidator()

            # Test 1: Valid CSV data validation
            valid_data = pd.DataFrame({
                'train_id': ['KMRL-001', 'KMRL-002'],
                'last_service_date': ['2024-09-01', '2024-09-15'],
                'fitness_cert_valid_from': ['2024-08-01', '2024-08-15'],
                'fitness_cert_valid_to': ['2024-11-01', '2024-11-15'],
                'jobcard_status': ['NONE', 'OPEN'],
                'mileage_since_overhaul': [45000, 52000],
                'crew_available': [True, True]
            })

            validation_result = validator.validate_csv_data(valid_data)
            tests.append(("Valid CSV data validation",
                         validation_result['valid']))

            if validation_result['valid']:
                tests.append(("Correct number of records processed", len(
                    validation_result['cleaned_data']) == 2))

            # Test 2: Invalid data handling
            invalid_data = pd.DataFrame({
                'train_id': ['INVALID-ID', 'KMRL-999'],
                'last_service_date': ['invalid-date', '2024-09-15'],
                # Expired certificate
                'fitness_cert_valid_to': ['2024-01-01', '2024-11-15'],
                'jobcard_status': ['CRITICAL_OPEN', 'NONE'],
                'mileage_since_overhaul': [-1000, 200000],  # Invalid mileage
            })

            invalid_validation = validator.validate_csv_data(invalid_data)
            tests.append(("Invalid data properly rejected",
                         not invalid_validation['valid']))
            tests.append(("Validation errors reported", len(
                invalid_validation.get('errors', [])) > 0))

            # Test 3: Business rule validation
            # Test minimum service capacity rule
            test_trains = []
            for i in range(25):
                test_trains.append({
                    'train_id': f'KMRL-{str(i+1).zfill(3)}',
                    'fitness_cert_valid_to': '2023-01-01',  # All expired
                    'jobcard_status': 'CRITICAL_OPEN',
                    'mileage_since_overhaul': 50000
                })

            business_validation = validator._validate_business_rules(
                test_trains)
            tests.append(("Business rules validation",
                         not business_validation['valid']))

        except ImportError as e:
            warnings.append(
                f"Could not import data_validation module: {str(e)}")
            tests.append(("Data validation module import", False))
        except Exception as e:
            tests.append(("Data validation functionality", False))
            warnings.append(f"Data validation test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_synthetic_data(self) -> Dict[str, Any]:
        """Test synthetic data generation"""

        tests = []
        warnings = []

        try:
            # Test synthetic data generation
            sys.path.append('data')
            from generate_synthetic_data import SyntheticDataGenerator

            generator = SyntheticDataGenerator()

            # Test 1: Generator initialization
            tests.append(("Generator initialized", generator.num_trains == 25))
            tests.append(
                ("Train IDs generated", len(generator.train_ids) == 25))

            # Test 2: Current train status generation
            train_status = generator.generate_current_train_status()
            tests.append(("Train status generated", len(train_status) == 25))

            # Validate train status structure
            if train_status:
                sample_train = train_status[0]
                required_fields = ['train_id', 'last_service_date', 'fitness_cert_valid_to',
                                   'jobcard_status', 'mileage_since_overhaul']
                has_all_fields = all(
                    field in sample_train for field in required_fields)
                tests.append(
                    ("Train status has required fields", has_all_fields))

                # Check service capability constraint
                service_capable = sum(1 for train in train_status
                                      if generator._is_service_capable(train))
                tests.append(
                    ("Minimum service capacity met", service_capable >= 18))

            # Test 3: Historical data generation
            historical_data = generator.generate_historical_performance()
            expected_records = 25 * 180  # 25 trains * 180 days
            tests.append(("Historical data generated",
                         len(historical_data) > 0))
            tests.append(("Correct historical data volume",
                         abs(len(historical_data) - expected_records) < 100))

            # Test 4: Complete dataset generation
            complete_dataset = generator.generate_complete_dataset()
            expected_components = ['trains', 'historical_performance', 'job_cards',
                                   'iot_sensors', 'branding_contracts', 'metadata']
            has_all_components = all(
                comp in complete_dataset for comp in expected_components)
            tests.append(("Complete dataset structure", has_all_components))

        except Exception as e:
            tests.append(("Synthetic data generation", False))
            warnings.append(f"Synthetic data test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_ml_predictions(self) -> Dict[str, Any]:
        """Test ML prediction functionality"""

        tests = []
        warnings = []

        try:
            sys.path.append('backend/models')
            from ml_predictor import DelayPredictor

            predictor = DelayPredictor()

            # Test 1: Model initialization
            await predictor.load_models()
            tests.append(("ML models loaded", predictor.is_trained))

            # Test 2: Single train prediction
            test_train = {
                'train_id': 'KMRL-001',
                'last_service_date': '2024-09-01',
                'fitness_cert_valid_to': '2024-12-01',
                'jobcard_status': 'NONE',
                'mileage_since_overhaul': 45000,
                'iot_sensor_flags': 'NORMAL',
                'crew_available': True
            }

            prediction = predictor.predict_individual_train(test_train)
            tests.append(("Individual prediction generated",
                         'delay_risk' in prediction))
            tests.append(("Prediction has confidence",
                         'confidence' in prediction))
            tests.append(("Risk factors identified",
                         'risk_factors' in prediction))

            # Validate prediction ranges
            if 'delay_risk' in prediction:
                delay_risk = prediction['delay_risk']
                tests.append(
                    ("Delay risk in valid range", 0 <= delay_risk <= 1))

            if 'maintenance_urgency' in prediction:
                maint_urgency = prediction['maintenance_urgency']
                tests.append(("Maintenance urgency in valid range",
                             0 <= maint_urgency <= 100))

            # Test 3: Batch prediction
            test_assignments = [test_train for _ in range(5)]
            batch_predictions = predictor.predict_performance(test_assignments)
            tests.append(("Batch predictions generated",
                         'individual_predictions' in batch_predictions))
            tests.append(("Aggregate metrics computed",
                         'aggregate_metrics' in batch_predictions))

        except Exception as e:
            tests.append(("ML prediction functionality", False))
            warnings.append(f"ML prediction test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_optimization_engine(self) -> Dict[str, Any]:
        """Test optimization algorithm performance"""

        tests = []
        warnings = []

        try:
            # Test optimization via API
            test_request = {
                "trains": [
                    {
                        "train_id": f"KMRL-{str(i).zfill(3)}",
                        "last_service_date": "2024-09-01",
                        "fitness_cert_valid_from": "2024-08-01",
                        "fitness_cert_valid_to": "2024-12-01",
                        "jobcard_status": "NONE" if i % 10 != 0 else "OPEN",
                        "mileage_since_overhaul": 40000 + i * 1000,
                        "crew_available": True,
                        "branding_exposure_hours": 0
                    } for i in range(1, 26)
                ],
                "target_date": "2024-10-02",
                "constraints": {
                    "min_service_trains": 18,
                    "maintenance_bays": 4,
                    "cleaning_bays": 3,
                    "available_crews": 22
                }
            }

            start_time = time.time()

            try:
                async with self.session.post(f"{self.api_base}/optimize",
                                             json=test_request) as response:
                    optimization_time = time.time() - start_time

                    if response.status == 200:
                        result = await response.json()
                        tests.append(("Optimization API accessible", True))

                        # Validate optimization result structure
                        required_fields = ['optimization_id',
                                           'assignments', 'objectives_achieved']
                        has_structure = all(
                            field in result for field in required_fields)
                        tests.append(
                            ("Optimization result structure", has_structure))

                        # Check assignments
                        if 'assignments' in result:
                            assignments = result['assignments']
                            tests.append(
                                ("All trains assigned", len(assignments) == 25))

                            service_count = sum(1 for a in assignments if a.get(
                                'assignment') == 'SERVICE')
                            tests.append(
                                ("Minimum service constraint met", service_count >= 18))

                            # Check assignment validity
                            valid_assignments = [
                                'SERVICE', 'STANDBY', 'MAINTENANCE']
                            all_valid = all(
                                a.get('assignment') in valid_assignments for a in assignments)
                            tests.append(("All assignments valid", all_valid))

                        # Check performance
                        tests.append(
                            ("Optimization completed quickly", optimization_time < 30))

                    else:
                        tests.append(("Optimization API accessible", False))
                        warnings.append(
                            f"Optimization API returned status {response.status}")

            except aiohttp.ClientError:
                tests.append(("Optimization API accessible", False))
                warnings.append("Could not connect to optimization API")

        except Exception as e:
            tests.append(("Optimization engine functionality", False))
            warnings.append(f"Optimization test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints"""

        tests = []
        warnings = []

        # Define endpoints to test
        endpoints = [
            ("GET", "/health", None, 200),
            ("GET", "/optimizations", None, 200),
            # Empty data might return validation error
            ("POST", "/predict", {"trains": []}, [200, 422]),
        ]

        for method, endpoint, data, expected_status in endpoints:
            try:
                if method == "GET":
                    async with self.session.get(f"{self.api_base}{endpoint}") as response:
                        if isinstance(expected_status, list):
                            success = response.status in expected_status
                        else:
                            success = response.status == expected_status
                        tests.append((f"{method} {endpoint}", success))

                elif method == "POST":
                    async with self.session.post(f"{self.api_base}{endpoint}",
                                                 json=data) as response:
                        if isinstance(expected_status, list):
                            success = response.status in expected_status
                        else:
                            success = response.status == expected_status
                        tests.append((f"{method} {endpoint}", success))

            except Exception as e:
                tests.append((f"{method} {endpoint}", False))
                warnings.append(
                    f"Endpoint {method} {endpoint} failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_what_if_simulation(self) -> Dict[str, Any]:
        """Test what-if simulation functionality"""

        tests = []
        warnings = []

        try:
            # First, run a base optimization
            base_request = {
                "trains": [
                    {
                        "train_id": "KMRL-001",
                        "last_service_date": "2024-09-01",
                        "fitness_cert_valid_to": "2024-12-01",
                        "jobcard_status": "NONE",
                        "mileage_since_overhaul": 45000,
                        "crew_available": True
                    }
                ],
                "target_date": "2024-10-02",
                "constraints": {"min_service_trains": 1}
            }

            base_optimization_id = None

            try:
                async with self.session.post(f"{self.api_base}/optimize",
                                             json=base_request) as response:
                    if response.status == 200:
                        base_result = await response.json()
                        base_optimization_id = base_result.get(
                            'optimization_id')
                        tests.append(
                            ("Base optimization for simulation", True))
                    else:
                        tests.append(
                            ("Base optimization for simulation", False))
            except:
                tests.append(("Base optimization for simulation", False))

            # Test what-if simulation
            if base_optimization_id:
                simulation_request = {
                    "base_optimization_id": base_optimization_id,
                    "modifications": {
                        "force_maintenance": ["KMRL-001"]
                    }
                }

                try:
                    async with self.session.post(f"{self.api_base}/simulate",
                                                 json=simulation_request) as response:
                        tests.append(("What-if simulation API",
                                     response.status in [200, 404]))

                        if response.status == 200:
                            sim_result = await response.json()
                            tests.append(
                                ("Simulation result structure", 'assignments' in sim_result))
                except:
                    tests.append(("What-if simulation API", False))
            else:
                tests.append(("What-if simulation API", False))
                warnings.append(
                    "Could not test simulation - base optimization failed")

        except Exception as e:
            tests.append(("What-if simulation functionality", False))
            warnings.append(f"What-if simulation test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_performance(self) -> Dict[str, Any]:
        """Test system performance and load handling"""

        tests = []
        warnings = []

        try:
            # Test 1: Response time for health check
            start_time = time.time()
            try:
                async with self.session.get(f"{self.api_base}/health") as response:
                    response_time = time.time() - start_time
                    tests.append(
                        ("Health check response time", response_time < 1.0))
            except:
                tests.append(("Health check response time", False))

            # Test 2: Concurrent requests handling
            async def make_request():
                try:
                    async with self.session.get(f"{self.api_base}/health") as response:
                        return response.status == 200
                except:
                    return False

            # Send 5 concurrent requests
            concurrent_tasks = [make_request() for _ in range(5)]
            results = await asyncio.gather(*concurrent_tasks)
            success_rate = sum(results) / len(results)
            tests.append(("Concurrent request handling", success_rate >= 0.8))

            # Test 3: Large dataset handling
            large_train_data = [
                {
                    "train_id": f"KMRL-{str(i).zfill(3)}",
                    "last_service_date": "2024-09-01",
                    "fitness_cert_valid_to": "2024-12-01",
                    "jobcard_status": "NONE",
                    "mileage_since_overhaul": 45000 + i * 100,
                    "crew_available": True
                } for i in range(1, 26)
            ]

            large_request = {
                "trains": large_train_data,
                "target_date": "2024-10-02",
                "constraints": {"min_service_trains": 18}
            }

            start_time = time.time()
            try:
                async with self.session.post(f"{self.api_base}/optimize",
                                             json=large_request) as response:
                    processing_time = time.time() - start_time
                    tests.append(
                        ("Large dataset processing", response.status == 200))
                    tests.append(
                        ("Large dataset performance", processing_time < 60))
            except:
                tests.append(("Large dataset processing", False))
                tests.append(("Large dataset performance", False))

        except Exception as e:
            tests.append(("Performance testing", False))
            warnings.append(f"Performance test failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and edge cases"""

        tests = []
        warnings = []

        # Test 1: Invalid JSON payload
        try:
            async with self.session.post(f"{self.api_base}/optimize",
                                         data="invalid json") as response:
                tests.append(("Invalid JSON handling",
                             response.status in [400, 422]))
        except:
            tests.append(("Invalid JSON handling", False))

        # Test 2: Missing required fields
        try:
            # Missing required fields
            incomplete_request = {"trains": [{"train_id": "KMRL-001"}]}
            async with self.session.post(f"{self.api_base}/optimize",
                                         json=incomplete_request) as response:
                tests.append(("Missing fields validation",
                             response.status in [400, 422]))
        except:
            tests.append(("Missing fields validation", False))

        # Test 3: Non-existent endpoint
        try:
            async with self.session.get(f"{self.api_base}/nonexistent") as response:
                tests.append(("404 error handling", response.status == 404))
        except:
            tests.append(("404 error handling", False))

        # Test 4: Impossible constraints
        try:
            impossible_request = {
                "trains": [{"train_id": "KMRL-001", "jobcard_status": "CRITICAL_OPEN"}],
                # Impossible with critical train
                "constraints": {"min_service_trains": 5}
            }
            async with self.session.post(f"{self.api_base}/optimize",
                                         json=impossible_request) as response:
                # Should either return an error or handle gracefully
                tests.append(("Impossible constraints handling",
                             response.status in [200, 400, 422]))
        except:
            tests.append(("Impossible constraints handling", False))

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    async def test_frontend_integration(self) -> Dict[str, Any]:
        """Test frontend integration"""

        tests = []
        warnings = []

        # Test 1: Frontend files exist
        frontend_files = [
            'frontend/index.html',
            'frontend/js/dashboard.js',
            'frontend/css/style.css'
        ]

        for file_path in frontend_files:
            tests.append(
                (f"Frontend file {file_path} exists", os.path.exists(file_path)))

        # Test 2: HTML structure validation
        try:
            if os.path.exists('frontend/index.html'):
                with open('frontend/index.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Check for essential elements
                required_elements = ['<title>', '<body>',
                                     'dashboard.js', 'style.css']
                for element in required_elements:
                    tests.append(
                        (f"HTML contains {element}", element in html_content))
        except Exception as e:
            tests.append(("HTML structure validation", False))
            warnings.append(f"HTML validation failed: {str(e)}")

        # Test 3: JavaScript functionality
        try:
            if os.path.exists('frontend/js/dashboard.js'):
                with open('frontend/js/dashboard.js', 'r', encoding='utf-8') as f:
                    js_content = f.read()

                # Check for essential functions
                required_functions = ['KMRLDashboard',
                                      'runOptimization', 'loadTrainData']
                for function in required_functions:
                    tests.append(
                        (f"JS contains {function}", function in js_content))
        except Exception as e:
            tests.append(("JavaScript functionality", False))
            warnings.append(f"JavaScript validation failed: {str(e)}")

        passed = sum(1 for _, result in tests if result)
        return {
            'success': passed == len(tests),
            'total_tests': len(tests),
            'tests_passed': passed,
            'details': tests,
            'warnings': warnings
        }

    def generate_test_report(self, overall_success: bool):
        """Generate comprehensive test report"""

        print("📊 TEST REPORT")
        print("=" * 60)
        print(
            f"Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        print(
            f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        total_tests = 0
        total_passed = 0

        for category, results in self.test_results.items():
            total_tests += results.get('total_tests', 0)
            total_passed += results.get('tests_passed', 0)

            status = "✅ PASS" if results.get('success') else "❌ FAIL"
            print(
                f"{status} {category}: {results.get('tests_passed', 0)}/{results.get('total_tests', 0)}")

            if results.get('warnings'):
                for warning in results['warnings']:
                    print(f"    ⚠️  {warning}")

        print()
        print(
            f"Summary: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")

        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_success': overall_success,
            'total_tests': total_tests,
            'total_passed': total_passed,
            'success_rate': total_passed/total_tests if total_tests > 0 else 0,
            'test_results': self.test_results
        }

        try:
            with open('test_report.json', 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"Detailed report saved to: test_report.json")
        except Exception as e:
            print(f"Could not save detailed report: {str(e)}")

        print()

        if overall_success:
            print("🎉 All tests passed! System is ready for demonstration.")
        else:
            print("🚨 Some tests failed. Please review and fix issues before demo.")


async def main():
    """Run the complete integration test suite"""

    tester = KMRLIntegrationTester()
    success = await tester.run_full_test_suite()

    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
