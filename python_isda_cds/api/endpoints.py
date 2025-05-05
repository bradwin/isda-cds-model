"""
FastAPI endpoints for the ISDA CDS Standard Model.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional

from ..models.curve import ZeroCurve, DayCountConvention, CompoundingBasis, InterpolationMethod
from ..models.cds import CDSPricer, CDSContract, CDSDate, CDSCouponInfo, bootstrap_spread_curve
from .models import (
    ZeroCurveModel, DiscountFactorRequestModel, ZeroRateRequestModel,
    ForwardRateRequestModel, CurveBuilderModel, CDSPricerModel,
    CDSContractModel, CreditCurveBuilderModel, UpfrontChargeRequestModel
)

router = APIRouter()

@router.post("/zero-curve", response_model=Dict[str, float])
async def create_zero_curve(curve_data: ZeroCurveModel):
    """
    Create a zero curve from dates and rates.
    
    Returns a mapping of dates to zero rates in the created curve.
    """
    try:
        # Convert model to Python objects
        base_date = curve_data.base_date.to_date()
        dates = [date_model.to_date() for date_model in curve_data.dates] if curve_data.dates else None
        rates = curve_data.rates if curve_data.rates else None
        
        # Create zero curve
        zero_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=curve_data.day_count_convention.value,
            compounding_basis=curve_data.compounding_basis.value
        )
        
        # Return a mapping of dates to rates for the created curve
        result = {
            point.date.isoformat(): point.rate 
            for point in zero_curve.rate_points
        }
        
        # Include base date
        result[base_date.isoformat()] = 0.0  # Base date always has zero rate
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating zero curve: {str(e)}")

@router.post("/discount-factor", response_model=float)
async def get_discount_factor(request: DiscountFactorRequestModel):
    """
    Get a discount factor for a specific date from a zero curve.
    """
    try:
        # Create zero curve from model
        base_date = request.curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.curve.dates] if request.curve.dates else None
        rates = request.curve.rates if request.curve.rates else None
        
        zero_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.curve.day_count_convention.value,
            compounding_basis=request.curve.compounding_basis.value
        )
        
        # Get target date
        target_date = request.target_date.to_date()
        
        # Calculate discount factor
        discount_factor = zero_curve.get_discount_factor(
            target_date=target_date,
            interpolation_method=request.interpolation_method.value
        )
        
        return discount_factor
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating discount factor: {str(e)}")

@router.post("/zero-rate", response_model=float)
async def get_zero_rate(request: ZeroRateRequestModel):
    """
    Get a zero rate for a specific date from a zero curve.
    """
    try:
        # Create zero curve from model
        base_date = request.curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.curve.dates] if request.curve.dates else None
        rates = request.curve.rates if request.curve.rates else None
        
        zero_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.curve.day_count_convention.value,
            compounding_basis=request.curve.compounding_basis.value
        )
        
        # Get target date
        target_date = request.target_date.to_date()
        
        # Calculate zero rate
        zero_rate = zero_curve.get_zero_rate(
            target_date=target_date,
            interpolation_method=request.interpolation_method.value
        )
        
        return zero_rate
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating zero rate: {str(e)}")

@router.post("/forward-rate", response_model=float)
async def get_forward_rate(request: ForwardRateRequestModel):
    """
    Get a forward rate between two dates from a zero curve.
    """
    try:
        # Create zero curve from model
        base_date = request.curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.curve.dates] if request.curve.dates else None
        rates = request.curve.rates if request.curve.rates else None
        
        zero_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.curve.day_count_convention.value,
            compounding_basis=request.curve.compounding_basis.value
        )
        
        # Get start and end dates
        start_date = request.start_date.to_date()
        end_date = request.end_date.to_date()
        
        # Calculate forward rate
        forward_rate = zero_curve.get_forward_rate(
            start_date=start_date,
            end_date=end_date,
            interpolation_method=request.interpolation_method.value
        )
        
        return forward_rate
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating forward rate: {str(e)}")

@router.post("/price-cds", response_model=Dict[str, float])
async def price_cds(request: CDSPricerModel):
    """
    Price a CDS contract using the ISDA CDS Standard Model.
    """
    try:
        # Create discount curve
        base_date = request.discount_curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.discount_curve.dates] if request.discount_curve.dates else None
        rates = request.discount_curve.rates if request.discount_curve.rates else None
        
        discount_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.discount_curve.day_count_convention.value,
            compounding_basis=request.discount_curve.compounding_basis.value
        )
        
        # Create survival curve
        base_date = request.survival_curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.survival_curve.dates] if request.survival_curve.dates else None
        rates = request.survival_curve.rates if request.survival_curve.rates else None
        
        survival_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.survival_curve.day_count_convention.value,
            compounding_basis=request.survival_curve.compounding_basis.value
        )
        
        # Create CDS contract
        cds_dates = CDSDate(
            trade_date=request.cds_contract.dates.trade_date.to_date(),
            effective_date=request.cds_contract.dates.effective_date.to_date(),
            maturity_date=request.cds_contract.dates.maturity_date.to_date(),
            value_date=request.cds_contract.dates.value_date.to_date(),
            settlement_date=request.cds_contract.dates.settlement_date.to_date(),
            step_in_date=request.cds_contract.dates.step_in_date.to_date()
        )
        
        cds_coupon_info = CDSCouponInfo(
            payment_frequency=request.cds_contract.coupon_info.payment_frequency,
            day_count_convention=request.cds_contract.coupon_info.day_count_convention.value,
            business_day_convention=request.cds_contract.coupon_info.business_day_convention.value,
            coupon_rate=request.cds_contract.coupon_info.coupon_rate
        )
        
        cds_contract = CDSContract(
            dates=cds_dates,
            coupon_info=cds_coupon_info,
            notional=request.cds_contract.notional,
            recovery_rate=request.cds_contract.recovery_rate,
            include_accrued_premium=request.cds_contract.include_accrued_premium,
            is_buy_protection=request.cds_contract.is_buy_protection
        )
        
        # Create CDS pricer
        cds_pricer = CDSPricer(
            discount_curve=discount_curve,
            survival_curve=survival_curve
        )
        
        # Price the CDS contract
        pricing_results = cds_pricer.price_cds(cds_contract)
        
        return pricing_results
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error pricing CDS contract: {str(e)}")

@router.post("/bootstrap-credit-curve", response_model=Dict[str, float])
async def bootstrap_credit_curve(request: CreditCurveBuilderModel):
    """
    Bootstrap a credit curve from CDS spreads.
    """
    try:
        # Create discount curve
        base_date = request.discount_curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.discount_curve.dates] if request.discount_curve.dates else None
        rates = request.discount_curve.rates if request.discount_curve.rates else None
        
        discount_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.discount_curve.day_count_convention.value,
            compounding_basis=request.discount_curve.compounding_basis.value
        )
        
        # Get valuation date
        valuation_date = request.valuation_date.to_date()
        
        # Extract CDS tenors and spreads
        cds_tenors = [item.tenor_years for item in request.cds_tenors_spreads]
        cds_spreads = [item.spread for item in request.cds_tenors_spreads]
        
        # Bootstrap credit curve
        credit_curve = bootstrap_spread_curve(
            discount_curve=discount_curve,
            valuation_date=valuation_date,
            cds_tenors=cds_tenors,
            cds_spreads=cds_spreads,
            recovery_rate=request.recovery_rate,
            cds_convention=request.cds_convention.value
        )
        
        # Return a mapping of dates to hazard rates
        result = {
            point.date.isoformat(): point.rate 
            for point in credit_curve.rate_points
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error bootstrapping credit curve: {str(e)}")

@router.post("/calculate-upfront", response_model=float)
async def calculate_upfront_charge(request: UpfrontChargeRequestModel):
    """
    Calculate the upfront charge for a CDS contract.
    """
    try:
        # Create discount curve
        base_date = request.discount_curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.discount_curve.dates] if request.discount_curve.dates else None
        rates = request.discount_curve.rates if request.discount_curve.rates else None
        
        discount_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.discount_curve.day_count_convention.value,
            compounding_basis=request.discount_curve.compounding_basis.value
        )
        
        # Create survival curve
        base_date = request.survival_curve.base_date.to_date()
        dates = [date_model.to_date() for date_model in request.survival_curve.dates] if request.survival_curve.dates else None
        rates = request.survival_curve.rates if request.survival_curve.rates else None
        
        survival_curve = ZeroCurve(
            base_date=base_date,
            dates=dates,
            rates=rates,
            day_count_convention=request.survival_curve.day_count_convention.value,
            compounding_basis=request.survival_curve.compounding_basis.value
        )
        
        # Create CDS contract
        cds_dates = CDSDate(
            trade_date=request.cds_contract.dates.trade_date.to_date(),
            effective_date=request.cds_contract.dates.effective_date.to_date(),
            maturity_date=request.cds_contract.dates.maturity_date.to_date(),
            value_date=request.cds_contract.dates.value_date.to_date(),
            settlement_date=request.cds_contract.dates.settlement_date.to_date(),
            step_in_date=request.cds_contract.dates.step_in_date.to_date()
        )
        
        cds_coupon_info = CDSCouponInfo(
            payment_frequency=request.cds_contract.coupon_info.payment_frequency,
            day_count_convention=request.cds_contract.coupon_info.day_count_convention.value,
            business_day_convention=request.cds_contract.coupon_info.business_day_convention.value,
            coupon_rate=request.cds_contract.coupon_info.coupon_rate
        )
        
        cds_contract = CDSContract(
            dates=cds_dates,
            coupon_info=cds_coupon_info,
            notional=request.cds_contract.notional,
            recovery_rate=request.cds_contract.recovery_rate,
            include_accrued_premium=request.cds_contract.include_accrued_premium,
            is_buy_protection=request.cds_contract.is_buy_protection
        )
        
        # Create CDS pricer
        cds_pricer = CDSPricer(
            discount_curve=discount_curve,
            survival_curve=survival_curve
        )
        
        # Calculate upfront charge
        upfront_charge = cds_pricer.calculate_upfront_charge(cds_contract)
        
        return upfront_charge
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating upfront charge: {str(e)}")
