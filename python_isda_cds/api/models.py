"""
Pydantic models for the API endpoints.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union
from datetime import date, datetime
from enum import Enum

class DayCountConventionEnum(str, Enum):
    ACT_365F = "ACT_365F"
    ACT_360 = "ACT_360"
    B30_360 = "30/360"
    B30E_360 = "30E/360"

class CompoundingBasisEnum(int, Enum):
    CONTINUOUS = 0
    ANNUAL = 1
    SEMI_ANNUAL = 2
    QUARTERLY = 4

class InterpolationMethodEnum(int, Enum):
    LINEAR_INTERP = 0
    LINEAR_FORWARDS = 1
    FLAT_FORWARDS = 2

class BadDayConventionEnum(str, Enum):
    NONE = "NONE"
    FOLLOW = "FOLLOW"
    MODIFIED_FOLLOW = "MODIFIED_FOLLOW"
    PREVIOUS = "PREVIOUS"

class InstrumentTypeEnum(str, Enum):
    MONEY_MARKET = "M"
    SWAP = "S"

class DateModel(BaseModel):
    """Model for representing dates in API requests."""
    year: int = Field(..., description="The year")
    month: int = Field(..., ge=1, le=12, description="The month (1-12)")
    day: int = Field(..., ge=1, le=31, description="The day (1-31)")
    
    @validator('day')
    def validate_day(cls, v, values):
        if 'year' not in values or 'month' not in values:
            return v
        
        year = values['year']
        month = values['month']
        
        # Validate day based on month and year
        if month in [4, 6, 9, 11] and v > 30:
            raise ValueError(f"Day {v} is invalid for month {month}")
        elif month == 2:
            # Check for leap year
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_day = 29 if is_leap else 28
            if v > max_day:
                raise ValueError(f"Day {v} is invalid for February in year {year}")
        
        return v
    
    def to_date(self) -> date:
        """Convert to Python date object."""
        return date(self.year, self.month, self.day)

class RatePointModel(BaseModel):
    """Model for a single point on the interest rate curve."""
    date: DateModel
    rate: float = Field(..., description="The zero rate")

class ZeroCurveModel(BaseModel):
    """Model for creating a zero curve."""
    base_date: DateModel = Field(..., description="The valuation date (curve base date)")
    dates: Optional[List[DateModel]] = Field(None, description="List of curve point dates")
    rates: Optional[List[float]] = Field(None, description="List of curve point rates")
    day_count_convention: DayCountConventionEnum = Field(DayCountConventionEnum.ACT_365F, 
                                                    description="Day count convention")
    compounding_basis: CompoundingBasisEnum = Field(CompoundingBasisEnum.ANNUAL, 
                                                description="Compounding basis")

class InstrumentModel(BaseModel):
    """Model for a market instrument used in curve building."""
    type: InstrumentTypeEnum
    date: DateModel
    rate: float = Field(..., description="The instrument rate")

class CurveBuilderModel(BaseModel):
    """Model for building a zero curve from market instruments."""
    valuation_date: DateModel = Field(..., description="The valuation date")
    instruments: List[InstrumentModel] = Field(..., description="List of market instruments")
    money_market_day_count: DayCountConventionEnum = Field(DayCountConventionEnum.ACT_360, 
                                                      description="Day count for money market instruments")
    fixed_swap_frequency: int = Field(2, description="Fixed leg frequency (payments per year)")
    float_swap_frequency: int = Field(4, description="Floating leg frequency (payments per year)")
    fixed_swap_day_count: DayCountConventionEnum = Field(DayCountConventionEnum.B30_360, 
                                                    description="Day count for fixed swap leg")
    float_swap_day_count: DayCountConventionEnum = Field(DayCountConventionEnum.ACT_360, 
                                                    description="Day count for floating swap leg")

class CDSDateModel(BaseModel):
    """Model for CDS contract dates."""
    trade_date: DateModel
    effective_date: DateModel
    maturity_date: DateModel
    value_date: DateModel
    settlement_date: DateModel
    step_in_date: DateModel

class CDSCouponInfoModel(BaseModel):
    """Model for CDS coupon structure."""
    payment_frequency: int = Field(..., description="Payments per year (e.g., 4 for quarterly)")
    day_count_convention: DayCountConventionEnum
    business_day_convention: BadDayConventionEnum
    coupon_rate: float = Field(..., description="Coupon rate in decimal (e.g., 0.05 for 5%)")

class CDSContractModel(BaseModel):
    """Model for a CDS contract."""
    dates: CDSDateModel
    coupon_info: CDSCouponInfoModel
    notional: float = Field(1000000.0, description="Notional amount of the contract")
    recovery_rate: float = Field(0.4, ge=0.0, le=1.0, description="Recovery rate in case of default")
    include_accrued_premium: bool = Field(True, description="Whether to include accrued premium in case of default")
    is_buy_protection: bool = Field(True, description="True if the contract is buying protection")

class CDSPricerModel(BaseModel):
    """Model for pricing a CDS contract."""
    discount_curve: ZeroCurveModel
    survival_curve: ZeroCurveModel
    cds_contract: CDSContractModel

class CDSTenorSpreadModel(BaseModel):
    """Model for a CDS tenor and spread pair."""
    tenor_years: float = Field(..., description="Tenor in years")
    spread: float = Field(..., description="CDS spread")

class CreditCurveBuilderModel(BaseModel):
    """Model for bootstrapping a credit curve from CDS spreads."""
    discount_curve: ZeroCurveModel
    valuation_date: DateModel
    cds_tenors_spreads: List[CDSTenorSpreadModel] = Field(..., description="List of CDS tenor/spread pairs")
    recovery_rate: float = Field(0.4, ge=0.0, le=1.0, description="Recovery rate assumption")
    cds_convention: DayCountConventionEnum = Field(DayCountConventionEnum.ACT_360, 
                                              description="Day count convention for CDS contracts")

class DiscountFactorRequestModel(BaseModel):
    """Model for requesting a discount factor from a curve."""
    curve: ZeroCurveModel
    target_date: DateModel
    interpolation_method: InterpolationMethodEnum = Field(InterpolationMethodEnum.FLAT_FORWARDS, 
                                                     description="Interpolation method")

class ZeroRateRequestModel(BaseModel):
    """Model for requesting a zero rate from a curve."""
    curve: ZeroCurveModel
    target_date: DateModel
    interpolation_method: InterpolationMethodEnum = Field(InterpolationMethodEnum.FLAT_FORWARDS, 
                                                     description="Interpolation method")

class ForwardRateRequestModel(BaseModel):
    """Model for requesting a forward rate between two dates."""
    curve: ZeroCurveModel
    start_date: DateModel
    end_date: DateModel
    interpolation_method: InterpolationMethodEnum = Field(InterpolationMethodEnum.FLAT_FORWARDS, 
                                                     description="Interpolation method")

class UpfrontChargeRequestModel(BaseModel):
    """Model for calculating the upfront charge for a CDS."""
    discount_curve: ZeroCurveModel
    survival_curve: ZeroCurveModel
    cds_contract: CDSContractModel
