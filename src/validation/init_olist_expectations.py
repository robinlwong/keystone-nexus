# init_olist_expectations.py
# Keystone Nexus - Data Quality Validation Suite
# Environment: AWS EC2 Ubuntu 24.04
# Run `pip install great_expectations pandas` before executing.

import great_expectations as gx
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.data_context import FileDataContext
import os


def create_logistics_expectation_suite():
    """
    Initializes a Great Expectations context and builds the 'olist_logistics_rules' 
    suite to prevent malformed telemetry from corrupting the Silver Lakehouse layer.
    
    This suite enforces the logical rules of space and time for logistics data:
    - Packages cannot be delivered before purchase (chronological integrity)
    - Order IDs must be unique and present (referential integrity)
    - Delivery estimates must be logically sound (business logic validation)
    - Order status must conform to known Olist states (data domain validation)
    """
    print("🚀 Initializing Great Expectations Context on Ubuntu 24.04...")
    
    # Set up the GX Data Context in the current directory (can be mapped to Airflow later)
    context_dir = os.path.join(os.getcwd(), "gx")
    context = FileDataContext.create(project_root_dir=context_dir)

    suite_name = "olist_logistics_rules"
    
    # Create a new expectation suite
    suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
    print(f"✅ Created Expectation Suite: {suite_name}")

    # -------------------------------------------------------------------------
    # Rule 1: Primary Key Integrity
    # Business Value: We cannot track delivery gaps if order IDs are missing or duplicated.
    # Impact: Prevents duplicate revenue counting and lost order tracking.
    # -------------------------------------------------------------------------
    expectation_order_id_not_null = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "order_id"},
        meta={
            "business_impact": "Critical - Lost orders cannot be tracked for fulfillment",
            "data_quality_dimension": "Completeness"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_order_id_not_null)

    expectation_order_id_unique = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "order_id"},
        meta={
            "business_impact": "Critical - Duplicate IDs cause double-counting revenue",
            "data_quality_dimension": "Uniqueness"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_order_id_unique)

    # -------------------------------------------------------------------------
    # Rule 2: Chronological Integrity (The "Time Travel" Check)
    # Business Value: A package cannot be delivered to a customer before it was purchased.
    # If this fails, there is a severe bug in the upstream e-commerce API.
    # Impact: Prevents nonsensical delivery lag calculations (e.g., "-5 days to deliver")
    # -------------------------------------------------------------------------
    expectation_delivery_after_purchase = ExpectationConfiguration(
        expectation_type="expect_column_pair_values_A_to_be_greater_than_B",
        kwargs={
            "column_A": "order_delivered_customer_date",
            "column_B": "order_purchase_timestamp",
            "ignore_row_if": "either_value_is_missing"  # Ignore active orders still in transit
        },
        meta={
            "business_impact": "High - Prevents impossible logistics metrics from reaching dashboards",
            "data_quality_dimension": "Validity (Temporal Logic)"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_delivery_after_purchase)

    # -------------------------------------------------------------------------
    # Rule 3: Validating the "Delivery Gap" Baseline
    # Business Value: Ensure the estimated delivery date is logically sound (after purchase).
    # This guarantees our Athena queries calculating "Estimated vs Actual" are accurate.
    # Impact: Accurate SLA tracking and customer satisfaction metrics.
    # -------------------------------------------------------------------------
    expectation_estimate_after_purchase = ExpectationConfiguration(
        expectation_type="expect_column_pair_values_A_to_be_greater_than_B",
        kwargs={
            "column_A": "order_estimated_delivery_date",
            "column_B": "order_purchase_timestamp",
        },
        meta={
            "business_impact": "Medium - Ensures SLA metrics are based on valid estimates",
            "data_quality_dimension": "Validity (Business Rule)"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_estimate_after_purchase)

    # -------------------------------------------------------------------------
    # Rule 4: Status Validation
    # Business Value: The order status must conform to known Olist states.
    # Prevents garbage strings from breaking dashboard aggregations.
    # Impact: Reliable order funnel analytics (created → delivered conversion rates)
    # -------------------------------------------------------------------------
    expectation_valid_status = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_in_set",
        kwargs={
            "column": "order_status",
            "value_set": [
                "created", "approved", "invoiced", "processing", 
                "shipped", "delivered", "unavailable", "canceled"
            ]
        },
        meta={
            "business_impact": "Medium - Prevents unknown statuses from breaking funnel reports",
            "data_quality_dimension": "Validity (Domain Constraint)"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_valid_status)

    # -------------------------------------------------------------------------
    # Rule 5: Revenue Integrity (Price must be non-negative)
    # Business Value: Ensures financial calculations are mathematically sound
    # Impact: Prevents negative revenue from corrupting P&L reports
    # -------------------------------------------------------------------------
    expectation_price_non_negative = ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={
            "column": "price",
            "min_value": 0,
            "max_value": None  # No upper limit (some luxury items can be very expensive)
        },
        meta={
            "business_impact": "Critical - Negative prices corrupt financial reporting",
            "data_quality_dimension": "Validity (Range Check)"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_price_non_negative)

    # -------------------------------------------------------------------------
    # Rule 6: Foreign Key Integrity (Customer ID must exist)
    # Business Value: Ensures referential integrity for customer analytics
    # Impact: Prevents orphaned orders from breaking customer segmentation
    # -------------------------------------------------------------------------
    expectation_customer_id_not_null = ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "customer_id"},
        meta={
            "business_impact": "High - Orphaned orders cannot be attributed to customers",
            "data_quality_dimension": "Completeness (Foreign Key)"
        }
    )
    suite.add_expectation(expectation_configuration=expectation_customer_id_not_null)

    # Save the suite to the GX context
    context.save_expectation_suite(expectation_suite=suite)
    print("🔒 Logistics Data Quality Rules locked and saved.")
    print("Pipeline is now protected against temporal data anomalies.")
    
    # Generate Data Docs for stakeholder review
    print("📊 Generating Data Docs HTML report...")
    context.build_data_docs()
    print("✅ Data quality report ready for executive review!")
    
    return context, suite


def validate_sample_data(context, suite_name, csv_path):
    """
    Run the expectation suite against a sample CSV file.
    
    Args:
        context: Great Expectations FileDataContext
        suite_name: Name of the expectation suite to use
        csv_path: Path to the CSV file to validate
    
    Returns:
        Validation results object
    """
    print(f"\n🔍 Validating sample data: {csv_path}")
    
    # Create a datasource for the CSV
    datasource = context.sources.add_pandas(name="olist_sample_datasource")
    asset = datasource.add_csv_asset(name="orders_csv", filepath_or_buffer=csv_path)
    
    # Create batch request
    batch_request = asset.build_batch_request()
    
    # Create checkpoint
    checkpoint = context.add_or_update_checkpoint(
        name="olist_validation_checkpoint",
        expectation_suite_name=suite_name,
        batch_request=batch_request,
    )
    
    # Run validation
    results = checkpoint.run()
    
    # Print summary
    if results["success"]:
        print("✅ All data quality checks PASSED!")
    else:
        print("❌ Data quality checks FAILED. Review Data Docs for details.")
        print(f"   Failed expectations: {results['statistics']['unsuccessful_expectations']}")
    
    return results


if __name__ == "__main__":
    print("=" * 70)
    print(" Keystone Nexus - Great Expectations Initialization")
    print(" Data Quality Enforcement for Olist E-Commerce Pipeline")
    print("=" * 70)
    print()
    
    # Create the expectation suite
    context, suite = create_logistics_expectation_suite()
    
    print()
    print("=" * 70)
    print(" Suite created successfully!")
    print(" Next steps:")
    print(" 1. Review Data Docs: open gx/uncommitted/data_docs/local_site/index.html")
    print(" 2. Run validation: validate_sample_data(context, 'olist_logistics_rules', 'path/to/orders.csv')")
    print(" 3. Integrate with Airflow: Use GreatExpectationsOperator in DAG")
    print("=" * 70)
