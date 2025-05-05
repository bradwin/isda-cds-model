"""
Zero curve implementation for the ISDA CDS Standard Model.
"""
import numpy as np
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Callable

class DayCountConvention:
    """Day count convention definitions"""
    ACT_365F = "ACT_365F"  # Actual/365 Fixed
    ACT_360 = "ACT_360"    # Actual/360
    B30_360 = "30/360"     # 30/360 Bond Basis
    B30E_360 = "30E/360"   # 30E/360 Eurobond Basis

class CompoundingBasis:
    """Compounding basis definitions"""
    ANNUAL = 1
    SEMI_ANNUAL = 2
    QUARTERLY = 4
    CONTINUOUS = 0  # Continuous compounding

class InterpolationMethod:
    """Interpolation method definitions"""
    LINEAR_INTERP = 0
    LINEAR_FORWARDS = 1
    FLAT_FORWARDS = 2

@dataclass
class RatePoint:
    """A single point on the interest rate curve"""
    date: date
    rate: float

class ZeroCurve:
    """
    Zero Curve implementation for the ISDA CDS Standard Model.
    
    This class represents a zero-coupon yield curve which can be used for
    discounting future cash flows to present value.
    """
    
    def __init__(self, 
                 base_date: date,
                 dates: List[date] = None,
                 rates: List[float] = None,
                 day_count_convention: str = DayCountConvention.ACT_365F,
                 compounding_basis: int = CompoundingBasis.ANNUAL):
        """
        Initialize a zero curve.
        
        Args:
            base_date: The valuation date (curve's anchor date)
            dates: List of dates for curve points
            rates: List of rates corresponding to the dates
            day_count_convention: Day count convention for rate calculation
            compounding_basis: Compounding basis (e.g., annual, semi-annual)
        """
        self.base_date = base_date
        self.day_count_convention = day_count_convention
        self.compounding_basis = compounding_basis
        
        # Initialize the curve points
        self.rate_points = []
        
        # Add initial points if provided
        if dates and rates:
            if len(dates) != len(rates):
                raise ValueError("Dates and rates lists must be the same length")
            
            for d, r in zip(dates, rates):
                self.add_rate(d, r)
    
    def add_rate(self, curve_date: date, rate: float) -> None:
        """
        Add a rate point to the curve.
        
        Args:
            curve_date: The date for this rate point
            rate: The zero rate at this date
        """
        if curve_date <= self.base_date:
            raise ValueError(f"Curve date {curve_date} must be after base date {self.base_date}")
        
        # Calculate the discount factor for this rate
        discount_factor = self._rate_to_discount(rate, curve_date)
        
        # Add to the array of rate points, keeping it sorted by date
        self.rate_points.append(RatePoint(date=curve_date, rate=rate))
        self.rate_points.sort(key=lambda x: x.date)
    
    def _rate_to_discount(self, rate: float, curve_date: date) -> float:
        """
        Convert a zero rate to a discount factor.
        
        Args:
            rate: The zero rate
            curve_date: The date associated with the rate
            
        Returns:
            The discount factor
        """
        # Calculate year fraction between base date and curve date
        year_fraction = self._year_fraction(self.base_date, curve_date)
        
        # Calculate discount factor based on compounding basis
        if self.compounding_basis == CompoundingBasis.CONTINUOUS:
            return np.exp(-rate * year_fraction)
        elif self.compounding_basis >= 1:
            return 1.0 / np.power(1.0 + rate / self.compounding_basis, 
                                  self.compounding_basis * year_fraction)
        else:
            raise ValueError(f"Unsupported compounding basis: {self.compounding_basis}")
    
    def _discount_to_rate(self, discount_factor: float, curve_date: date) -> float:
        """
        Convert a discount factor to a zero rate.
        
        Args:
            discount_factor: The discount factor
            curve_date: The date associated with the discount factor
            
        Returns:
            The zero rate
        """
        # Calculate year fraction between base date and curve date
        year_fraction = self._year_fraction(self.base_date, curve_date)
        
        # Calculate rate based on compounding basis
        if year_fraction <= 0:
            raise ValueError("Year fraction must be positive")
            
        if self.compounding_basis == CompoundingBasis.CONTINUOUS:
            return -np.log(discount_factor) / year_fraction
        elif self.compounding_basis >= 1:
            return self.compounding_basis * (np.power(discount_factor, -1.0 / (self.compounding_basis * year_fraction)) - 1.0)
        else:
            raise ValueError(f"Unsupported compounding basis: {self.compounding_basis}")
    
    def _year_fraction(self, start_date: date, end_date: date) -> float:
        """
        Calculate the year fraction between two dates based on the day count convention.
        
        Args:
            start_date: The start date
            end_date: The end date
            
        Returns:
            The year fraction
        """
        days = (end_date - start_date).days
        
        if self.day_count_convention == DayCountConvention.ACT_365F:
            return days / 365.0
        elif self.day_count_convention == DayCountConvention.ACT_360:
            return days / 360.0
        elif self.day_count_convention == DayCountConvention.B30_360:
            # Implement 30/360 Bond Basis calculation
            # This is a simplified version
            y1, m1, d1 = start_date.year, start_date.month, start_date.day
            y2, m2, d2 = end_date.year, end_date.month, end_date.day
            
            # Adjust day counts according to 30/360 rules
            if d1 == 31: 
                d1 = 30
            if d2 == 31 and d1 == 30: 
                d2 = 30
                
            return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0
        else:
            raise ValueError(f"Unsupported day count convention: {self.day_count_convention}")
    
    def get_discount_factor(self, target_date: date, 
                          interpolation_method: int = InterpolationMethod.FLAT_FORWARDS) -> float:
        """
        Get the discount factor for a specific date.
        
        Args:
            target_date: The date for which to get the discount factor
            interpolation_method: The interpolation method to use
            
        Returns:
            The discount factor
        """
        if not self.rate_points:
            raise ValueError("Zero curve has no rate points")
        
        if target_date <= self.base_date:
            # For dates on or before the base date, return 1.0
            return 1.0
        
        # Find the surrounding rate points for interpolation
        if target_date >= self.rate_points[-1].date:
            # If beyond the last point, use the last rate (flat extrapolation)
            return self._rate_to_discount(self.rate_points[-1].rate, target_date)
        
        if target_date <= self.rate_points[0].date:
            # If before the first point, use the first rate (flat extrapolation)
            return self._rate_to_discount(self.rate_points[0].rate, target_date)
        
        # Find the surrounding points for interpolation
        for i in range(1, len(self.rate_points)):
            if self.rate_points[i].date >= target_date:
                lower_point = self.rate_points[i-1]
                upper_point = self.rate_points[i]
                break
        
        # Interpolate based on the selected method
        if interpolation_method == InterpolationMethod.LINEAR_INTERP:
            # Linear rate interpolation
            t = (target_date - lower_point.date).days / (upper_point.date - lower_point.date).days
            rate = lower_point.rate + t * (upper_point.rate - lower_point.rate)
            return self._rate_to_discount(rate, target_date)
            
        elif interpolation_method == InterpolationMethod.FLAT_FORWARDS:
            # Flat forward interpolation
            discount_lower = self._rate_to_discount(lower_point.rate, lower_point.date)
            discount_upper = self._rate_to_discount(upper_point.rate, upper_point.date)
            
            # Calculate discount factor assuming flat forwards
            t_lower = (lower_point.date - self.base_date).days
            t_upper = (upper_point.date - self.base_date).days
            t_target = (target_date - self.base_date).days
            
            # Apply flat forward formula
            t_ratio = (t_target - t_lower) / (t_upper - t_lower)
            discount = discount_lower * np.power(discount_upper / discount_lower, t_ratio)
            return discount
            
        elif interpolation_method == InterpolationMethod.LINEAR_FORWARDS:
            # Linear forward interpolation (more complex)
            # This is a simplified implementation
            discount_lower = self._rate_to_discount(lower_point.rate, lower_point.date)
            discount_upper = self._rate_to_discount(upper_point.rate, upper_point.date)
            
            # Calculate the implied forward rates
            t_lower = self._year_fraction(self.base_date, lower_point.date)
            t_upper = self._year_fraction(self.base_date, upper_point.date)
            t_target = self._year_fraction(self.base_date, target_date)
            
            # Convert to forward rates and interpolate
            fwd_lower = -np.log(discount_lower) / t_lower
            fwd_upper = -np.log(discount_upper) / t_upper
            
            # Linearly interpolate the forward rates
            t_ratio = (t_target - t_lower) / (t_upper - t_lower)
            fwd = fwd_lower + t_ratio * (fwd_upper - fwd_lower)
            
            # Convert back to discount factor
            return np.exp(-fwd * t_target)
        
        else:
            raise ValueError(f"Unsupported interpolation method: {interpolation_method}")
    
    def get_zero_rate(self, target_date: date, 
                    interpolation_method: int = InterpolationMethod.FLAT_FORWARDS) -> float:
        """
        Get the zero rate for a specific date.
        
        Args:
            target_date: The date for which to get the zero rate
            interpolation_method: The interpolation method to use
            
        Returns:
            The zero rate
        """
        discount_factor = self.get_discount_factor(target_date, interpolation_method)
        return self._discount_to_rate(discount_factor, target_date)
    
    def get_forward_rate(self, start_date: date, end_date: date, 
                       interpolation_method: int = InterpolationMethod.FLAT_FORWARDS) -> float:
        """
        Calculate the forward rate between two dates.
        
        Args:
            start_date: The start date of the forward period
            end_date: The end date of the forward period
            interpolation_method: The interpolation method to use
            
        Returns:
            The forward rate
        """
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
        
        # Get the discount factors for both dates
        discount_start = self.get_discount_factor(start_date, interpolation_method)
        discount_end = self.get_discount_factor(end_date, interpolation_method)
        
        # Calculate the forward discount factor
        forward_discount = discount_end / discount_start
        
        # Convert to a rate
        year_fraction = self._year_fraction(start_date, end_date)
        
        if self.compounding_basis == CompoundingBasis.CONTINUOUS:
            return -np.log(forward_discount) / year_fraction
        elif self.compounding_basis >= 1:
            return self.compounding_basis * (np.power(forward_discount, -1.0 / (self.compounding_basis * year_fraction)) - 1.0)
        else:
            raise ValueError(f"Unsupported compounding basis: {self.compounding_basis}")

def build_zero_curve_from_instruments(
    valuation_date: date,
    instrument_types: List[str],
    instrument_dates: List[date],
    instrument_rates: List[float],
    money_market_day_count: str = DayCountConvention.ACT_360,
    fixed_swap_frequency: int = 2,  # Semi-annual
    float_swap_frequency: int = 4,  # Quarterly
    fixed_swap_day_count: str = DayCountConvention.B30_360,
    float_swap_day_count: str = DayCountConvention.ACT_360
) -> ZeroCurve:
    """
    Build a zero curve from market instruments.
    
    Args:
        valuation_date: The valuation date (curve base date)
        instrument_types: List of instrument types ('M' for money market, 'S' for swap)
        instrument_dates: List of instrument maturity dates
        instrument_rates: List of instrument rates
        money_market_day_count: Day count convention for money market instruments
        fixed_swap_frequency: Payment frequency for fixed swap leg (per year)
        float_swap_frequency: Payment frequency for floating swap leg (per year)
        fixed_swap_day_count: Day count convention for fixed swap leg
        float_swap_day_count: Day count convention for floating swap leg
        
    Returns:
        A ZeroCurve object
    """
    if len(instrument_types) != len(instrument_dates) or len(instrument_types) != len(instrument_rates):
        raise ValueError("Instrument types, dates, and rates must have the same length")
    
    # Initialize an empty curve
    curve = ZeroCurve(base_date=valuation_date)
    
    # Separate instruments by type
    cash_dates = []
    cash_rates = []
    swap_dates = []
    swap_rates = []
    
    for instr_type, instr_date, instr_rate in zip(instrument_types, instrument_dates, instrument_rates):
        if instr_type.upper() == 'M':  # Money market
            cash_dates.append(instr_date)
            cash_rates.append(instr_rate)
        elif instr_type.upper() == 'S':  # Swap
            swap_dates.append(instr_date)
            swap_rates.append(instr_rate)
        else:
            raise ValueError(f"Unknown instrument type: {instr_type}. Use 'M' for money market or 'S' for swap.")
    
    # Add money market instruments (simplified implementation)
    for date, rate in zip(cash_dates, cash_rates):
        # For money market instruments, convert from simple interest to zero rate
        year_fraction = (date - valuation_date).days / 365.0  # Simplified
        if money_market_day_count == DayCountConvention.ACT_360:
            year_fraction = (date - valuation_date).days / 360.0
            
        # Convert from money market rate to discount factor
        discount_factor = 1.0 / (1.0 + rate * year_fraction)
        
        # Convert to zero rate and add to curve
        if curve.compounding_basis == CompoundingBasis.ANNUAL:
            zero_rate = (np.power(discount_factor, -1.0 / year_fraction) - 1.0)
        else:
            zero_rate = -np.log(discount_factor) / year_fraction  # Continuous compounding
            
        curve.add_rate(date, zero_rate)
    
    # Add swap instruments (simplified implementation)
    # Note: A full implementation would involve bootstrapping the swap rates
    for date, rate in zip(swap_dates, swap_rates):
        # This is a very simplified approach - would need proper bootstrapping in practice
        # We're just adding the swap rates as zero rates for illustration
        curve.add_rate(date, rate)
    
    return curve
