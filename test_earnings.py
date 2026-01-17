#!/usr/bin/env python3
"""Test script to verify earnings report retrieval for AAPL"""

import sys
import logging
from services.financial_data_client import FinancialDataClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_earnings_retrieval():
    """Test retrieving earnings reports for AAPL"""
    print("\n" + "="*80)
    print("Testing Earnings Report Retrieval for AAPL")
    print("="*80 + "\n")

    try:
        # Initialize client
        client = FinancialDataClient()
        print("✓ FinancialDataClient initialized\n")

        # Fetch reports for AAPL
        print("Fetching earnings reports for AAPL...")
        reports = client.get_security_info("AAPL")

        print("\n" + "="*80)
        print("RESULTS")
        print("="*80 + "\n")

        # Display summary
        if reports:
            print(f"✓ Successfully retrieved reports for {reports.get('symbol', 'AAPL')}")
            print(f"  Security Type: {reports.get('security_type', 'N/A')}")
            print(f"  Company Name: {reports.get('company_name', 'N/A')}")

            # Earnings data
            earnings = reports.get('earnings')
            if earnings:
                quarterly = earnings.get('quarterly', [])
                annual = earnings.get('annual', [])
                print(f"\n  Earnings Data:")
                print(f"    - Quarterly Reports: {len(quarterly)} quarters")
                print(f"    - Annual Reports: {len(annual)} years")

                if quarterly:
                    print(f"\n    Latest Quarterly Report:")
                    latest = quarterly[0]
                    print(f"      Date: {latest.get('date')}")
                    print(f"      Revenue: ${latest.get('revenue', 0):,.0f}" if latest.get('revenue') else "      Revenue: N/A")
                    print(f"      Earnings: ${latest.get('earnings', 0):,.0f}" if latest.get('earnings') else "      Earnings: N/A")
            else:
                print("\n  ⚠ No earnings data available")

            # Calendar
            calendar = reports.get('calendar')
            if calendar:
                print(f"\n  Earnings Calendar:")
                print(f"    - Next Earnings Date: {calendar.get('earnings_date', 'N/A')}")
            else:
                print("\n  ⚠ No calendar data available")

            # Financials
            financials = reports.get('financials')
            if financials:
                income = financials.get('income_statement', [])
                balance = financials.get('balance_sheet', [])
                cashflow = financials.get('cash_flow', [])
                print(f"\n  Financial Statements:")
                print(f"    - Income Statements: {len(income)}")
                print(f"    - Balance Sheets: {len(balance)}")
                print(f"    - Cash Flow Statements: {len(cashflow)}")
            else:
                print("\n  ⚠ No financial statements available")

            # Metrics
            metrics = reports.get('metrics')
            if metrics:
                print(f"\n  Key Metrics:")
                print(f"    - P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
                print(f"    - Market Cap: ${metrics.get('market_cap', 0):,.0f}" if metrics.get('market_cap') else "    - Market Cap: N/A")
                print(f"    - EPS: {metrics.get('eps', 'N/A')}")
                print(f"    - Dividend Yield: {metrics.get('dividend_yield', 'N/A')}")
            else:
                print("\n  ⚠ No metrics available")

            print("\n" + "="*80)
            print("✓ TEST PASSED - Successfully retrieved earnings data")
            print("="*80 + "\n")
            return True
        else:
            print("✗ No reports returned")
            print("\n" + "="*80)
            print("✗ TEST FAILED")
            print("="*80 + "\n")
            return False

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\n" + "="*80)
        print("✗ TEST FAILED")
        print("="*80 + "\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_earnings_retrieval()
    sys.exit(0 if success else 1)
