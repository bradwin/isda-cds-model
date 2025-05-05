# Python Implementation of ISDA CDS Standard Model

This project is a Python implementation of the ISDA CDS Standard Model, a standardized method for pricing Credit Default Swaps (CDS) developed by the International Swaps and Derivatives Association (ISDA).

## Overview

The ISDA CDS Standard Model is widely used in the financial industry to ensure consistency in CDS pricing. This Python implementation provides:

1. Core financial models for interest rate curve construction
2. Credit curve bootstrapping from market spreads
3. CDS pricing using industry-standard methodologies
4. A REST API for integration with other applications
5. Swagger UI documentation for easy exploration

## Features

- **Zero Curve Construction**: Build interest rate curves from money market and swap instruments
- **Credit Curve Bootstrapping**: Create survival probability curves from market CDS spreads
- **CDS Pricing**: Calculate mark-to-market values, par spreads, and upfront charges
- **Interpolation Methods**: Linear rate, flat forward, and linear forward interpolation
- **Day Count Conventions**: Support for ACT/365F, ACT/360, 30/360, and more
- **RESTful API**: Access all functionality via HTTP endpoints
- **Interactive Documentation**: Explore the API with Swagger UI

## Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/python-isda-cds.git
cd python-isda-cds

# Build and run Docker container
docker build -t isda-cds-api .
docker run -p 8000:8000 isda-cds-api
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/python-isda-cds.git
cd python-isda-cds

# Install dependencies
pip install -r python_isda_cds/requirements.txt

# Run the API server
python -m python_isda_cds.main
```

## API Documentation

Once the server is running, access the Swagger UI documentation at:

```
http://localhost:8000/docs
```

This provides an interactive interface to explore and test all API endpoints.

## API Endpoints

### Interest Rate Curves

- `POST /api/zero-curve`: Create a zero curve from dates and rates
- `POST /api/discount-factor`: Get a discount factor for a specific date
- `POST /api/zero-rate`: Get a zero rate for a specific date
- `POST /api/forward-rate`: Get a forward rate between two dates

### CDS Pricing

- `POST /api/price-cds`: Price a CDS contract
- `POST /api/bootstrap-credit-curve`: Bootstrap a credit curve from CDS spreads
- `POST /api/calculate-upfront`: Calculate the upfront charge for a CDS contract

## Code Structure

- `python_isda_cds/models/`: Core financial models
  - `curve.py`: Zero curve implementation
  - `cds.py`: CDS pricing models
- `python_isda_cds/api/`: REST API implementation
  - `models.py`: Pydantic models for API requests/responses
  - `endpoints.py`: API endpoint handlers
- `python_isda_cds/main.py`: Main application entry point

## Usage Examples

### Building a Zero Curve

```python
from python_isda_cds.models.curve import ZeroCurve, DayCountConvention, CompoundingBasis
from datetime import date

# Create a zero curve
curve = ZeroCurve(
    base_date=date(2025, 5, 5),
    dates=[date(2025, 11, 5), date(2026, 5, 5), date(2027, 5, 5), date(2030, 5, 5)],
    rates=[0.03, 0.035, 0.04, 0.045],
    day_count_convention=DayCountConvention.ACT_365F,
    compounding_basis=CompoundingBasis.ANNUAL
)

# Get a discount factor
discount_factor = curve.get_discount_factor(date(2026, 1, 5))
print(f"Discount factor: {discount_factor}")

# Get a zero rate
zero_rate = curve.get_zero_rate(date(2028, 5, 5))
print(f"Zero rate: {zero_rate}")
```

### Pricing a CDS Contract

```python
from python_isda_cds.models.curve import ZeroCurve
from python_isda_cds.models.cds import CDSPricer, CDSContract, CDSDate, CDSCouponInfo, BadDayConvention
from datetime import date

# Create discount curve and survival curve
discount_curve = ZeroCurve(...)
survival_curve = ZeroCurve(...)

# Create CDS contract
cds_dates = CDSDate(
    trade_date=date(2025, 5, 5),
    effective_date=date(2025, 5, 7),
    maturity_date=date(2030, 5, 7),
    value_date=date(2025, 5, 7),
    settlement_date=date(2025, 5, 9),
    step_in_date=date(2025, 5, 8)
)

cds_coupon_info = CDSCouponInfo(
    payment_frequency=4,  # Quarterly
    day_count_convention="ACT_360",
    business_day_convention=BadDayConvention.MODIFIED_FOLLOW,
    coupon_rate=0.01  # 100 bps
)

cds_contract = CDSContract(
    dates=cds_dates,
    coupon_info=cds_coupon_info,
    notional=10000000.0,
    recovery_rate=0.4,
    include_accrued_premium=True,
    is_buy_protection=True
)

# Price the CDS contract
cds_pricer = CDSPricer(discount_curve, survival_curve)
result = cds_pricer.price_cds(cds_contract)
print(f"Mark-to-market value: {result['mark_to_market']}")
print(f"Par spread: {result['par_spread']}")
```

## License

This software is released under the ISDA CDS Standard Model Public License.

## Acknowledgements

This Python implementation is based on the original C/C++ code developed by ISDA and Markit.