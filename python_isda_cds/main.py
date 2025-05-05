"""
Main application module for the ISDA CDS Standard Model REST API.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import json
from datetime import date

from python_isda_cds.api.endpoints import router

# Create FastAPI application
app = FastAPI(
    title="ISDA CDS Standard Model API",
    description="""
    # ISDA CDS Standard Model API
    
    This API provides access to the Python implementation of the ISDA CDS Standard Model, which is a standardized 
    method for pricing Credit Default Swaps (CDS) developed by the International Swaps and Derivatives Association (ISDA).
    
    ## Key Features
    
    * **Interest Rate Curve Construction** - Build zero curves from market instruments
    * **Credit Curve Bootstrapping** - Create survival probability curves from market CDS spreads
    * **CDS Pricing** - Calculate mark-to-market values, par spreads, and upfront charges
    * **Multiple Interpolation Methods** - Linear, flat forward, and linear forward interpolation
    * **Various Day Count Conventions** - Support for ACT/365F, ACT/360, 30/360, and more
    
    ## Getting Started
    
    1. Use the `/api/zero-curve` endpoint to create an interest rate curve
    2. Use the `/api/bootstrap-credit-curve` endpoint to create a credit curve
    3. Use the `/api/price-cds` endpoint to price a CDS contract
    
    For more details on each endpoint, refer to the documentation below.
    """,
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Sample data for the API examples
example_date = date(2025, 5, 5)  # Current date from context
sample_data = {
    "zero_curve": {
        "base_date": {"year": 2025, "month": 5, "day": 5},
        "dates": [
            {"year": 2025, "month": 11, "day": 5},
            {"year": 2026, "month": 5, "day": 5},
            {"year": 2027, "month": 5, "day": 5},
            {"year": 2030, "month": 5, "day": 5}
        ],
        "rates": [0.03, 0.035, 0.04, 0.045],
        "day_count_convention": "ACT_365F",
        "compounding_basis": 1
    },
    "credit_curve": {
        "base_date": {"year": 2025, "month": 5, "day": 5},
        "dates": [
            {"year": 2025, "month": 5, "day": 5},
            {"year": 2026, "month": 5, "day": 5},
            {"year": 2027, "month": 5, "day": 5},
            {"year": 2028, "month": 5, "day": 5},
            {"year": 2030, "month": 5, "day": 5}
        ],
        "rates": [0.0, 0.01, 0.015, 0.018, 0.02],
        "day_count_convention": "ACT_365F",
        "compounding_basis": 0
    },
    "cds_contract": {
        "dates": {
            "trade_date": {"year": 2025, "month": 5, "day": 5},
            "effective_date": {"year": 2025, "month": 5, "day": 7},
            "maturity_date": {"year": 2030, "month": 5, "day": 7},
            "value_date": {"year": 2025, "month": 5, "day": 7},
            "settlement_date": {"year": 2025, "month": 5, "day": 9},
            "step_in_date": {"year": 2025, "month": 5, "day": 8}
        },
        "coupon_info": {
            "payment_frequency": 4,
            "day_count_convention": "ACT_360",
            "business_day_convention": "MODIFIED_FOLLOW",
            "coupon_rate": 0.01
        },
        "notional": 10000000.0,
        "recovery_rate": 0.4,
        "include_accrued_premium": True,
        "is_buy_protection": True
    },
    "instrument_examples": [
        {"type": "M", "date": {"year": 2025, "month": 6, "day": 5}, "rate": 0.025},
        {"type": "M", "date": {"year": 2025, "month": 8, "day": 5}, "rate": 0.028},
        {"type": "M", "date": {"year": 2025, "month": 11, "day": 5}, "rate": 0.03},
        {"type": "S", "date": {"year": 2026, "month": 5, "day": 5}, "rate": 0.035},
        {"type": "S", "date": {"year": 2027, "month": 5, "day": 5}, "rate": 0.04},
        {"type": "S", "date": {"year": 2030, "month": 5, "day": 5}, "rate": 0.045}
    ],
    "cds_tenor_spread_examples": [
        {"tenor_years": 1.0, "spread": 0.01},
        {"tenor_years": 2.0, "spread": 0.015},
        {"tenor_years": 3.0, "spread": 0.018},
        {"tenor_years": 5.0, "spread": 0.02}
    ]
}

# Custom OpenAPI schema to improve documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ISDA CDS Standard Model API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add additional info to schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.isda.org/wp-content/uploads/2018/02/isda-logo.png"
    }
    
    # Enhance endpoint descriptions with examples and detailed info
    if "paths" in openapi_schema:
        # Zero Curve endpoint
        if "/api/zero-curve" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/zero-curve"]["post"]["description"] = """
            ## Create a Zero Curve
            
            Creates a zero-coupon interest rate curve from a set of dates and rates. This curve can be used for
            discounting future cash flows to present value, which is a fundamental component of CDS pricing.
            
            ### Underlying Logic
            
            The zero curve implementation follows the ISDA standard approach for constructing interest rate curves:
            
            1. Each point in the curve consists of a date and a zero rate
            2. For a given date, the zero rate represents the yield of a zero-coupon bond maturing on that date
            3. Rates are stored in the specified day count convention and compounding basis
            4. Internal calculations convert between discount factors and zero rates as needed using the formula:
               - For annual compounding: `DF = 1 / (1 + r*t)` where r is the rate and t is the year fraction
               - For continuous compounding: `DF = exp(-r*t)`
            5. The curve can be used to discount any cash flow to present value using: `PV = CF * DF`
            
            The implementation extends from the C/C++ version in the ISDA CDS Standard Model where 
            zero curves are represented by the TCurve structure with date-rate pairs.
            
            ### Input Parameters
            
            - **base_date**: The valuation date (anchor date for the curve)
            - **dates**: List of dates for curve points (tenors)
            - **rates**: List of zero rates corresponding to the dates
            - **day_count_convention**: Method for calculating year fractions (e.g., ACT/365F)
            - **compounding_basis**: Compounding frequency (e.g., Annual = 1, Semi-Annual = 2)
            
            ### Output
            
            A mapping of dates to zero rates in the created curve.
            
            ### Example
            
            ```json
            {
              "base_date": {"year": 2025, "month": 5, "day": 5},
              "dates": [
                {"year": 2025, "month": 11, "day": 5},
                {"year": 2026, "month": 5, "day": 5},
                {"year": 2027, "month": 5, "day": 5},
                {"year": 2030, "month": 5, "day": 5}
              ],
              "rates": [0.03, 0.035, 0.04, 0.045],
              "day_count_convention": "ACT_365F",
              "compounding_basis": 1
            }
            ```
            """
            openapi_schema["paths"]["/api/zero-curve"]["post"]["requestBody"]["content"]["application/json"]["example"] = sample_data["zero_curve"]
        
        # Discount Factor endpoint
        if "/api/discount-factor" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/discount-factor"]["post"]["description"] = """
            ## Get a Discount Factor
            
            Calculates a discount factor for a specific date based on a zero curve. Discount factors represent
            the present value of a unit payment in the future and are essential for pricing financial instruments.
            
            ### Underlying Logic
            
            The discount factor calculation applies the core time value of money concept:
            
            1. First, the API identifies the surrounding curve points that bracket the target date
            2. It then applies the chosen interpolation method between those points:
               - **Linear Interpolation**: Directly interpolates rates between points
               - **Flat Forward Interpolation**: Assumes constant forward rates between points (ISDA standard approach)
               - **Linear Forward Interpolation**: Assumes linearly changing forward rates
            3. The interpolated rate is then converted to a discount factor using:
               - For annual compounding: `DF = 1 / (1 + r)^t` where r is the rate and t is the year fraction
               - For continuous compounding: `DF = exp(-r*t)`
            
            The flat forward approach follows the ISDA model's implementation in `InterpRateDiscountFactors` and 
            `JpmcdsZCInterpolate` functions, which calculate discount factors by interpolating between adjacent curve points.
            
            ### Input Parameters
            
            - **curve**: The zero curve definition
            - **target_date**: The date for which to calculate the discount factor
            - **interpolation_method**: Method to use for interpolation between curve points
            
            ### Output
            
            The discount factor value as a float.
            
            ### Example
            
            ```json
            {
              "curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "target_date": {"year": 2026, "month": 1, "day": 5},
              "interpolation_method": 2
            }
            ```
            """
            openapi_schema["paths"]["/api/discount-factor"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "curve": sample_data["zero_curve"],
                "target_date": {"year": 2026, "month": 1, "day": 5},
                "interpolation_method": 2
            }
        
        # Zero Rate endpoint
        if "/api/zero-rate" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/zero-rate"]["post"]["description"] = """
            ## Get a Zero Rate
            
            Calculates a zero rate for a specific date based on a zero curve. Zero rates represent
            the yield of a zero-coupon bond with a given maturity date.
            
            ### Underlying Logic
            
            The zero rate calculation follows these steps:
            
            1. First, a discount factor is obtained for the target date using the interpolation method specified
            2. This discount factor represents the present value of 1 unit paid at the target date
            3. The discount factor is then converted back to a zero rate using:
               - For annual compounding: `r = (1/DF)^(1/t) - 1` where DF is the discount factor and t is the time
               - For continuous compounding: `r = -ln(DF)/t`
            
            This approach mirrors the C++ implementation in functions like `JpmcdsDiscountToRate` in the ISDA model,
            which handles various compounding frequencies and day count conventions when converting between
            discount factors and rates.
            
            ### Input Parameters
            
            - **curve**: The zero curve definition
            - **target_date**: The date for which to calculate the zero rate
            - **interpolation_method**: Method to use for interpolation between curve points
            
            ### Output
            
            The zero rate value as a float.
            
            ### Example
            
            ```json
            {
              "curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "target_date": {"year": 2028, "month": 5, "day": 5},
              "interpolation_method": 2
            }
            ```
            """
            openapi_schema["paths"]["/api/zero-rate"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "curve": sample_data["zero_curve"],
                "target_date": {"year": 2028, "month": 5, "day": 5},
                "interpolation_method": 2
            }
        
        # Forward Rate endpoint
        if "/api/forward-rate" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/forward-rate"]["post"]["description"] = """
            ## Get a Forward Rate
            
            Calculates a forward rate between two dates based on a zero curve. Forward rates represent
            the implied interest rate between two future dates.
            
            ### Underlying Logic
            
            The forward rate calculation follows the approach in the ISDA model's `JpmcdsForwardFromZCurve` function:
            
            1. Get discount factors for both the start date (DF₁) and end date (DF₂) using curve interpolation
            2. Calculate the forward discount factor as the ratio: FDF = DF₂/DF₁
            3. This represents the discount factor for the period between start date and end date
            4. Convert this forward discount factor to a rate using the formula:
               - For annual compounding: `r = (1/FDF)^(1/t) - 1` where t is the period length
               - For continuous compounding: `r = -ln(FDF)/t`
            
            The implementation ensures no-arbitrage relationships are maintained between spot rates
            and forward rates across the curve, which is fundamental to the ISDA model's approach to building
            consistent interest rate term structures.
            
            ### Input Parameters
            
            - **curve**: The zero curve definition
            - **start_date**: The start date of the forward period
            - **end_date**: The end date of the forward period
            - **interpolation_method**: Method to use for interpolation between curve points
            
            ### Output
            
            The forward rate value as a float.
            
            ### Example
            
            ```json
            {
              "curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "start_date": {"year": 2026, "month": 5, "day": 5},
              "end_date": {"year": 2027, "month": 5, "day": 5},
              "interpolation_method": 2
            }
            ```
            """
            openapi_schema["paths"]["/api/forward-rate"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "curve": sample_data["zero_curve"],
                "start_date": {"year": 2026, "month": 5, "day": 5},
                "end_date": {"year": 2027, "month": 5, "day": 5},
                "interpolation_method": 2
            }
        
        # Price CDS endpoint
        if "/api/price-cds" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/price-cds"]["post"]["description"] = """
            ## Price a CDS Contract
            
            Prices a Credit Default Swap (CDS) contract according to the ISDA CDS Standard Model methodology.
            This calculates the present value of both the premium and protection legs, as well as other metrics.
            
            ### Underlying Logic
            
            The CDS pricing follows the ISDA CDS Standard Model methodology implemented in functions like
            `JpmcdsCdsPrice` and `JpmcdsPremiumLegPV` in the original C/C++ code:
            
            1. **Premium Leg Valuation**:
               - Generate a schedule of premium payment dates based on the contract frequency
               - For each payment date:
                 - Calculate the survival probability to that date (using the survival curve)
                 - Calculate the discount factor for that date (using the discount curve)
                 - Calculate the premium amount (notional × coupon rate × day count fraction)
                 - Sum the PV of all payments: premium × discount factor × survival probability
            
            2. **Protection Leg Valuation**:
               - For each interval between payment dates:
                 - Calculate the probability of default during that period using survival probabilities
                 - Use a midpoint approximation to estimate when default occurs in each period
                 - Calculate the loss given default: notional × (1 - recovery rate)
                 - Sum the PV of all protection payments: LGD × default probability × discount factor
            
            3. **Par Spread Calculation**:
               - The spread that makes the premium leg PV equal to the protection leg PV
               - Calculated by dividing protection leg PV by the risky PV01 (premium leg PV with 1% coupon)
            
            This implementation mirrors the precise risk-neutral valuation model defined in the ISDA CDS Standard Model,
            which became the market standard following the "CDS Big Bang" protocol in 2009.
            
            ### Input Parameters
            
            - **discount_curve**: The interest rate curve for discounting cash flows
            - **survival_curve**: The survival probability curve (credit curve)
            - **cds_contract**: The CDS contract specification including dates, coupon info, and recovery rate
            
            ### Output
            
            A dictionary with the following pricing results:
            - **premium_leg_pv**: Present value of the premium leg
            - **protection_leg_pv**: Present value of the protection leg
            - **mark_to_market**: Mark-to-market value of the contract
            - **par_spread**: Par spread (break-even spread)
            - **risky_pv01**: Risk measure representing the price value of a 1 basis point change in spread
            
            ### Example
            
            ```json
            {
              "discount_curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5},
                  {"year": 2030, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04, 0.045],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "survival_curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 5, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5},
                  {"year": 2028, "month": 5, "day": 5},
                  {"year": 2030, "month": 5, "day": 5}
                ],
                "rates": [0.0, 0.01, 0.015, 0.018, 0.02],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 0
              },
              "cds_contract": {
                "dates": {
                  "trade_date": {"year": 2025, "month": 5, "day": 5},
                  "effective_date": {"year": 2025, "month": 5, "day": 7},
                  "maturity_date": {"year": 2030, "month": 5, "day": 7},
                  "value_date": {"year": 2025, "month": 5, "day": 7},
                  "settlement_date": {"year": 2025, "month": 5, "day": 9},
                  "step_in_date": {"year": 2025, "month": 5, "day": 8}
                },
                "coupon_info": {
                  "payment_frequency": 4,
                  "day_count_convention": "ACT_360",
                  "business_day_convention": "MODIFIED_FOLLOW",
                  "coupon_rate": 0.01
                },
                "notional": 10000000.0,
                "recovery_rate": 0.4,
                "include_accrued_premium": true,
                "is_buy_protection": true
              }
            }
            ```
            """
            openapi_schema["paths"]["/api/price-cds"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "discount_curve": sample_data["zero_curve"],
                "survival_curve": sample_data["credit_curve"],
                "cds_contract": sample_data["cds_contract"]
            }
        
        # Bootstrap Credit Curve endpoint
        if "/api/bootstrap-credit-curve" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/bootstrap-credit-curve"]["post"]["description"] = """
            ## Bootstrap a Credit Curve
            
            Bootstraps a credit curve (survival probability curve) from market CDS spreads. This curve
            represents the market-implied probability of default over time and is essential for pricing CDS.
            
            ### Underlying Logic
            
            The credit curve bootstrapping process in this API implements the ISDA model's approach found in
            functions like `JpmcdsCreditCurveImplied` and `cdsbootstrap.c`:
            
            1. The algorithm uses an iterative bootstrapping procedure:
               - Start with a flat hazard rate of zero at valuation date (100% survival probability)
               - For each CDS tenor/spread pair, working from shortest to longest:
                 - Calculate the implied hazard rate that makes the CDS price to par at the given spread
                 - This involves solving for the hazard rate that makes premium leg PV = protection leg PV
                 - Add this point to the survival curve
            
            2. The hazard rate (h) represents the instantaneous probability of default and relates to
               survival probability (S) through the formula: `S(t) = exp(-h*t)` in the constant hazard rate model
            
            3. The process uses:
               - The interest rate curve (discount curve) for discounting cash flows
               - Recovery rate assumption (typically 40%) to determine loss given default
               - Day count conventions specific to CDS contracts
            
            This implementation is a simplified version of the ISDA model's bootstrap procedure, which uses
            more sophisticated root-finding methods in the original C++ implementation to ensure a consistent
            and arbitrage-free credit curve.
            
            ### Input Parameters
            
            - **discount_curve**: The interest rate curve for discounting
            - **valuation_date**: The valuation date
            - **cds_tenors_spreads**: List of CDS tenors and spreads (market quotes)
            - **recovery_rate**: The recovery rate assumption (typically 0.4 or 40%)
            - **cds_convention**: The day count convention for CDS contracts
            
            ### Output
            
            A mapping of dates to hazard rates in the bootstrapped credit curve.
            
            ### Example
            
            ```json
            {
              "discount_curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5},
                  {"year": 2030, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04, 0.045],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "valuation_date": {"year": 2025, "month": 5, "day": 5},
              "cds_tenors_spreads": [
                {"tenor_years": 1.0, "spread": 0.01},
                {"tenor_years": 2.0, "spread": 0.015},
                {"tenor_years": 3.0, "spread": 0.018},
                {"tenor_years": 5.0, "spread": 0.02}
              ],
              "recovery_rate": 0.4,
              "cds_convention": "ACT_360"
            }
            ```
            """
            openapi_schema["paths"]["/api/bootstrap-credit-curve"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "discount_curve": sample_data["zero_curve"],
                "valuation_date": {"year": 2025, "month": 5, "day": 5},
                "cds_tenors_spreads": sample_data["cds_tenor_spread_examples"],
                "recovery_rate": 0.4,
                "cds_convention": "ACT_360"
            }
        
        # Calculate Upfront Charge endpoint
        if "/api/calculate-upfront" in openapi_schema["paths"]:
            openapi_schema["paths"]["/api/calculate-upfront"]["post"]["description"] = """
            ## Calculate Upfront Charge
            
            Calculates the upfront charge (or payment) for a CDS contract. This is the amount that
            needs to be paid at the start of the contract to make it fair given the market conditions.
            
            ### Underlying Logic
            
            The upfront charge calculation is based on the approach in the ISDA Standard Model's
            `CalcUpfrontCharge` function and follows the post-2009 "CDS Big Bang" market convention:
            
            1. Calculate the present value of both legs of the CDS:
               - Premium leg PV: Expected value of all future premium payments
               - Protection leg PV: Expected value of the contingent default payment
            
            2. The upfront charge is the difference: Upfront = Protection leg PV - Premium leg PV
            
            3. The sign convention:
               - Positive value: Protection buyer pays upfront to protection seller
               - Negative value: Protection seller pays upfront to protection buyer
            
            4. The amount depends on the difference between:
               - The contractual coupon rate specified in the CDS contract
               - The par spread (fair spread) implied by the market
            
            This approach matches the standardized CDS trading convention established after the "CDS Big Bang"
            where most CDS contracts trade with fixed coupon rates (typically 100bps or 500bps) and an
            upfront payment to adjust for the actual credit risk.
            
            ### Input Parameters
            
            - **discount_curve**: The interest rate curve for discounting
            - **survival_curve**: The survival probability curve (credit curve)
            - **cds_contract**: The CDS contract specification
            
            ### Output
            
            The upfront charge as a float. A positive value means the protection buyer pays,
            and a negative value means the protection seller pays.
            
            ### Example
            
            ```json
            {
              "discount_curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 11, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5},
                  {"year": 2030, "month": 5, "day": 5}
                ],
                "rates": [0.03, 0.035, 0.04, 0.045],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 1
              },
              "survival_curve": {
                "base_date": {"year": 2025, "month": 5, "day": 5},
                "dates": [
                  {"year": 2025, "month": 5, "day": 5},
                  {"year": 2026, "month": 5, "day": 5},
                  {"year": 2027, "month": 5, "day": 5},
                  {"year": 2028, "month": 5, "day": 5},
                  {"year": 2030, "month": 5, "day": 5}
                ],
                "rates": [0.0, 0.01, 0.015, 0.018, 0.02],
                "day_count_convention": "ACT_365F",
                "compounding_basis": 0
              },
              "cds_contract": {
                "dates": {
                  "trade_date": {"year": 2025, "month": 5, "day": 5},
                  "effective_date": {"year": 2025, "month": 5, "day": 7},
                  "maturity_date": {"year": 2030, "month": 5, "day": 7},
                  "value_date": {"year": 2025, "month": 5, "day": 7},
                  "settlement_date": {"year": 2025, "month": 5, "day": 9},
                  "step_in_date": {"year": 2025, "month": 5, "day": 8}
                },
                "coupon_info": {
                  "payment_frequency": 4,
                  "day_count_convention": "ACT_360",
                  "business_day_convention": "MODIFIED_FOLLOW",
                  "coupon_rate": 0.05
                },
                "notional": 10000000.0,
                "recovery_rate": 0.4,
                "include_accrued_premium": true,
                "is_buy_protection": true
              }
            }
            ```
            """
            openapi_schema["paths"]["/api/calculate-upfront"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
                "discount_curve": sample_data["zero_curve"],
                "survival_curve": sample_data["credit_curve"],
                "cds_contract": {
                    **sample_data["cds_contract"],
                    "coupon_info": {
                        **sample_data["cds_contract"]["coupon_info"],
                        "coupon_rate": 0.05  # Higher coupon rate to demonstrate upfront charge
                    }
                }
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Root endpoint with basic info
@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint with basic information about the API.
    """
    return {
        "name": "ISDA CDS Standard Model API",
        "version": "1.0.0",
        "description": "Python implementation of the ISDA CDS Standard Model",
        "documentation": "/docs",
    }

# Run the application when executed directly
if __name__ == "__main__":
    uvicorn.run("python_isda_cds.main:app", host="0.0.0.0", port=8000, reload=True)