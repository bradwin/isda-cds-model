"""
Credit Default Swap (CDS) model implementation for the ISDA CDS Standard Model.
"""
import numpy as np
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union

from .curve import ZeroCurve, InterpolationMethod

class BadDayConvention:
    """Bad day conventions for adjusting dates that fall on weekends or holidays"""
    NONE = "NONE"
    FOLLOW = "FOLLOW"
    MODIFIED_FOLLOW = "MODIFIED_FOLLOW"
    PREVIOUS = "PREVIOUS"
    
class StubType:
    """Stub type definitions for handling odd periods in schedules"""
    FRONT_SHORT = "FRONT_SHORT"
    FRONT_LONG = "FRONT_LONG"
    BACK_SHORT = "BACK_SHORT"
    BACK_LONG = "BACK_LONG"

@dataclass
class CDSDate:
    """Representation of CDS contract dates"""
    trade_date: date
    effective_date: date
    maturity_date: date
    value_date: date
    settlement_date: date
    step_in_date: date

@dataclass
class Payment:
    """Representation of a CDS payment"""
    payment_date: date
    amount: float
    day_count_fraction: float

@dataclass
class CDSCouponInfo:
    """Information about the CDS coupon structure"""
    payment_frequency: int  # Payments per year (e.g., 4 for quarterly)
    day_count_convention: str
    business_day_convention: str
    coupon_rate: float  # In decimal (e.g., 0.05 for 5%)

class CDSContract:
    """
    Class representing a Credit Default Swap contract.
    
    This class encapsulates the terms and attributes of a CDS contract.
    """
    
    def __init__(self, 
                 dates: CDSDate,
                 coupon_info: CDSCouponInfo,
                 notional: float = 1000000.0,
                 recovery_rate: float = 0.4,
                 include_accrued_premium: bool = True,
                 is_buy_protection: bool = True):
        """
        Initialize a CDS contract.
        
        Args:
            dates: The important dates for the CDS contract
            coupon_info: Information about the coupon structure
            notional: The notional amount of the contract
            recovery_rate: The assumed recovery rate in case of default (0.0-1.0)
            include_accrued_premium: Whether to include accrued premium in case of default
            is_buy_protection: True if the contract is buying protection
        """
        self.dates = dates
        self.coupon_info = coupon_info
        self.notional = notional
        self.recovery_rate = recovery_rate
        self.include_accrued_premium = include_accrued_premium
        self.is_buy_protection = is_buy_protection
        
        # Validate inputs
        if recovery_rate < 0.0 or recovery_rate > 1.0:
            raise ValueError("Recovery rate must be between 0.0 and 1.0")
        
        if dates.maturity_date <= dates.effective_date:
            raise ValueError("Maturity date must be after effective date")

    def _generate_schedule(self) -> List[date]:
        """
        Generate the payment schedule for the CDS contract.
        
        Returns:
            List of payment dates
        """
        frequency = self.coupon_info.payment_frequency
        months_per_period = 12 // frequency
        
        payment_dates = []
        current_date = self.dates.effective_date
        
        while current_date < self.dates.maturity_date:
            # Move forward by the payment frequency
            year = current_date.year
            month = current_date.month + months_per_period
            
            # Handle month overflow
            if month > 12:
                year += month // 12
                month = month % 12
                if month == 0:
                    month = 12
                    year -= 1
                    
            # Last payment is exactly on maturity date
            next_date = date(year, month, current_date.day)
            if next_date >= self.dates.maturity_date:
                payment_dates.append(self.dates.maturity_date)
                break
                
            payment_dates.append(next_date)
            current_date = next_date
        
        # Add maturity date if it's not already included
        if payment_dates[-1] != self.dates.maturity_date:
            payment_dates.append(self.dates.maturity_date)
        
        return payment_dates
    
    def _adjust_for_business_days(self, dates: List[date], holiday_calendar=None) -> List[date]:
        """
        Adjust dates for business days according to the convention.
        
        Args:
            dates: List of dates to adjust
            holiday_calendar: Optional calendar of holidays
            
        Returns:
            List of adjusted dates
        """
        # This is a simplified implementation without a full holiday calendar
        adjusted_dates = []
        
        for d in dates:
            adjusted = d
            
            # Check if the date is a weekend
            is_weekend = adjusted.weekday() >= 5  # Saturday or Sunday
            
            # Check if the date is a holiday
            is_holiday = False
            if holiday_calendar and adjusted in holiday_calendar:
                is_holiday = True
                
            if not is_weekend and not is_holiday:
                adjusted_dates.append(adjusted)
                continue
                
            # Adjust according to convention
            if self.coupon_info.business_day_convention == BadDayConvention.FOLLOW:
                while is_weekend or is_holiday:
                    adjusted += timedelta(days=1)
                    is_weekend = adjusted.weekday() >= 5
                    is_holiday = holiday_calendar and adjusted in holiday_calendar
                    
            elif self.coupon_info.business_day_convention == BadDayConvention.MODIFIED_FOLLOW:
                original_month = adjusted.month
                while is_weekend or is_holiday:
                    adjusted += timedelta(days=1)
                    is_weekend = adjusted.weekday() >= 5
                    is_holiday = holiday_calendar and adjusted in holiday_calendar
                    
                # If the month changed, go backwards instead
                if adjusted.month != original_month:
                    adjusted = d
                    while is_weekend or is_holiday:
                        adjusted -= timedelta(days=1)
                        is_weekend = adjusted.weekday() >= 5
                        is_holiday = holiday_calendar and adjusted in holiday_calendar
                    
            elif self.coupon_info.business_day_convention == BadDayConvention.PREVIOUS:
                while is_weekend or is_holiday:
                    adjusted -= timedelta(days=1)
                    is_weekend = adjusted.weekday() >= 5
                    is_holiday = holiday_calendar and adjusted in holiday_calendar
            
            # If NONE, we keep the original date
            
            adjusted_dates.append(adjusted)
        
        return adjusted_dates
    
    def _calculate_day_count_fractions(self, 
                                     dates: List[date], 
                                     start_date: date) -> List[float]:
        """
        Calculate day count fractions between consecutive dates.
        
        Args:
            dates: List of period end dates
            start_date: Starting date for the first period
            
        Returns:
            List of day count fractions
        """
        fractions = []
        previous_date = start_date
        
        for current_date in dates:
            if self.coupon_info.day_count_convention == "ACT_360":
                fraction = (current_date - previous_date).days / 360.0
            elif self.coupon_info.day_count_convention == "ACT_365F":
                fraction = (current_date - previous_date).days / 365.0
            elif self.coupon_info.day_count_convention == "30/360":
                # Simplified 30/360 calculation
                y1, m1, d1 = previous_date.year, previous_date.month, previous_date.day
                y2, m2, d2 = current_date.year, current_date.month, current_date.day
                
                # Adjustments for 30/360
                if d1 == 31:
                    d1 = 30
                if d2 == 31 and d1 == 30:
                    d2 = 30
                    
                days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
                fraction = days / 360.0
            else:
                raise ValueError(f"Unsupported day count convention: {self.coupon_info.day_count_convention}")
            
            fractions.append(fraction)
            previous_date = current_date
            
        return fractions
    
    def generate_premium_leg_cashflows(self) -> List[Payment]:
        """
        Generate the premium leg cashflows of the CDS contract.
        
        Returns:
            List of premium payments
        """
        # Generate payment schedule
        payment_dates = self._generate_schedule()
        
        # Adjust for business days
        adjusted_dates = self._adjust_for_business_days(payment_dates)
        
        # Calculate day count fractions
        day_count_fractions = self._calculate_day_count_fractions(adjusted_dates, self.dates.effective_date)
        
        # Calculate premium payments
        payments = []
        for i, (payment_date, day_count_fraction) in enumerate(zip(adjusted_dates, day_count_fractions)):
            # Skip payments before the value date
            if payment_date < self.dates.value_date:
                continue
                
            # Calculate payment amount
            amount = self.notional * self.coupon_info.coupon_rate * day_count_fraction
            
            # Create payment
            payment = Payment(
                payment_date=payment_date,
                amount=amount,
                day_count_fraction=day_count_fraction
            )
            
            payments.append(payment)
            
        return payments

class CDSPricer:
    """
    Class for pricing CDS contracts according to the ISDA CDS Standard Model.
    """
    
    def __init__(self, discount_curve: ZeroCurve, survival_curve: ZeroCurve):
        """
        Initialize a CDS pricer.
        
        Args:
            discount_curve: The interest rate zero curve for discounting cash flows
            survival_curve: The survival probability curve (credit curve)
        """
        self.discount_curve = discount_curve
        self.survival_curve = survival_curve
    
    def price_cds(self, cds: CDSContract) -> Dict[str, float]:
        """
        Price a CDS contract.
        
        Args:
            cds: The CDS contract to price
            
        Returns:
            Dictionary with pricing results
        """
        # Calculate PV of premium leg
        premium_leg = self._calculate_premium_leg_pv(cds)
        
        # Calculate PV of contingent leg (protection)
        protection_leg = self._calculate_protection_leg_pv(cds)
        
        # Calculate mark-to-market value
        if cds.is_buy_protection:
            mtm = premium_leg - protection_leg
        else:
            mtm = protection_leg - premium_leg
        
        # Calculate par spread
        par_spread = self._calculate_par_spread(cds)
        
        # Calculate risky PV01
        risky_pv01 = premium_leg / cds.coupon_info.coupon_rate
        
        # Return results
        return {
            "premium_leg_pv": premium_leg,
            "protection_leg_pv": protection_leg,
            "mark_to_market": mtm,
            "par_spread": par_spread,
            "risky_pv01": risky_pv01
        }
    
    def _calculate_premium_leg_pv(self, cds: CDSContract) -> float:
        """
        Calculate the present value of the premium leg.
        
        Args:
            cds: The CDS contract
            
        Returns:
            The present value of the premium leg
        """
        premium_payments = cds.generate_premium_leg_cashflows()
        
        pv = 0.0
        for payment in premium_payments:
            # Calculate discount factor
            discount_factor = self.discount_curve.get_discount_factor(payment.payment_date)
            
            # Calculate survival probability
            survival_prob = self.survival_curve.get_discount_factor(payment.payment_date)
            
            # PV of premium payment
            pv += payment.amount * discount_factor * survival_prob
        
        # For a clean price, we'd need to adjust for accrued premium
        # This is a simplified implementation
        
        return pv
    
    def _calculate_protection_leg_pv(self, cds: CDSContract) -> float:
        """
        Calculate the present value of the protection leg.
        
        Args:
            cds: The CDS contract
            
        Returns:
            The present value of the protection leg
        """
        # Get payment schedule (we'll use this for the protection leg too)
        premium_payments = cds.generate_premium_leg_cashflows()
        
        # Loss given default
        lgd = (1.0 - cds.recovery_rate) * cds.notional
        
        pv = 0.0
        previous_date = cds.dates.value_date
        previous_survival = self.survival_curve.get_discount_factor(previous_date)
        
        for payment in premium_payments:
            # Calculate discount factor for this period
            discount_factor = self.discount_curve.get_discount_factor(payment.payment_date)
            
            # Calculate survival probability
            current_survival = self.survival_curve.get_discount_factor(payment.payment_date)
            
            # Probability of default during this period
            default_prob = previous_survival - current_survival
            
            # Simplified assumption: default occurs at midpoint of period
            midpoint = previous_date + (payment.payment_date - previous_date) / 2
            midpoint_discount = self.discount_curve.get_discount_factor(midpoint)
            
            # PV of protection payment
            pv += lgd * default_prob * midpoint_discount
            
            # Update for next period
            previous_date = payment.payment_date
            previous_survival = current_survival
        
        return pv
    
    def _calculate_par_spread(self, cds: CDSContract) -> float:
        """
        Calculate the par spread of the CDS contract.
        
        Args:
            cds: The CDS contract
            
        Returns:
            The par spread in decimal form
        """
        # Create a temporary CDS with 1.0 spread
        temp_coupon_info = CDSCouponInfo(
            payment_frequency=cds.coupon_info.payment_frequency,
            day_count_convention=cds.coupon_info.day_count_convention,
            business_day_convention=cds.coupon_info.business_day_convention,
            coupon_rate=1.0  # Using 1.0 for easy scaling
        )
        
        temp_cds = CDSContract(
            dates=cds.dates,
            coupon_info=temp_coupon_info,
            notional=cds.notional,
            recovery_rate=cds.recovery_rate,
            include_accrued_premium=cds.include_accrued_premium,
            is_buy_protection=cds.is_buy_protection
        )
        
        # Calculate PV of premium leg with 1.0 spread for scaling
        premium_pv = self._calculate_premium_leg_pv(temp_cds)
        
        # Calculate PV of protection leg
        protection_pv = self._calculate_protection_leg_pv(cds)
        
        # Par spread is the spread that makes the PVs equal
        if premium_pv > 0:
            par_spread = protection_pv / premium_pv
        else:
            par_spread = 0.0
            
        return par_spread
    
    def calculate_upfront_charge(self, cds: CDSContract) -> float:
        """
        Calculate the upfront charge for a CDS contract.
        
        Args:
            cds: The CDS contract
            
        Returns:
            The upfront charge
        """
        pricing_results = self.price_cds(cds)
        upfront = pricing_results["protection_leg_pv"] - pricing_results["premium_leg_pv"]
        
        # For a buy protection position, a positive upfront means the buyer pays
        if not cds.is_buy_protection:
            upfront = -upfront
            
        return upfront

def bootstrap_spread_curve(
    discount_curve: ZeroCurve,
    valuation_date: date,
    cds_tenors: List[int],  # in years
    cds_spreads: List[float],
    recovery_rate: float = 0.4,
    cds_convention: str = "ACT_360"
) -> ZeroCurve:
    """
    Bootstrap a survival probability curve from CDS spreads.
    
    Args:
        discount_curve: The interest rate curve for discounting
        valuation_date: The valuation date
        cds_tenors: List of CDS tenors in years
        cds_spreads: List of market CDS spreads corresponding to the tenors
        recovery_rate: The recovery rate assumption
        cds_convention: The day count convention for CDS contracts
        
    Returns:
        A survival probability curve (credit curve)
    """
    # Simplified implementation - in practice, this would be a more complex bootstrapping process
    base_date = valuation_date
    survival_dates = []
    survival_rates = []
    
    # Add a point at the valuation date with survival probability 1.0
    survival_dates.append(base_date)
    survival_rates.append(0.0)  # Zero hazard rate = 100% survival
    
    # For each tenor/spread pair, calculate an implied survival probability
    for years, spread in zip(cds_tenors, cds_spreads):
        # Calculate the maturity date
        days = int(years * 365)
        maturity = base_date + timedelta(days=days)
        
        # Calculate a simplified hazard rate (constant hazard rate assumption)
        # This is a very simplified model - a real implementation would use more sophisticated bootstrapping
        loss_given_default = 1.0 - recovery_rate
        hazard_rate = spread / loss_given_default
        
        survival_dates.append(maturity)
        survival_rates.append(hazard_rate)
    
    # Create a survival curve
    survival_curve = ZeroCurve(
        base_date=base_date,
        dates=survival_dates,
        rates=survival_rates,
        day_count_convention="ACT_365F",  # Typically ACT_365F for hazard rates
        compounding_basis=0  # Continuous for hazard rates
    )
    
    return survival_curve
