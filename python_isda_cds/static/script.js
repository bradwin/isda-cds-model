// API endpoint definitions with their schema and examples
const apiEndpoints = {
    'zero-curve': {
        title: 'Create Zero Curve',
        endpoint: '/api/zero-curve',
        method: 'POST',
        description: `
            <p>Creates a zero-coupon interest rate curve from a set of dates and rates. This curve can be used for
            discounting future cash flows to present value, which is a fundamental component of CDS pricing.</p>
            
            <h4>Underlying Logic</h4>
            <p>The zero curve implementation follows the ISDA standard approach for constructing interest rate curves:</p>
            <ul>
                <li>Each point in the curve consists of a date and a zero rate</li>
                <li>For a given date, the zero rate represents the yield of a zero-coupon bond maturing on that date</li>
                <li>Rates are stored in the specified day count convention and compounding basis</li>
                <li>Internal calculations convert between discount factors and zero rates as needed</li>
                <li>The curve can be used to discount any cash flow to present value using: PV = CF * DF</li>
            </ul>
        `,
        fieldDescriptions: {
            'base_date': 'The valuation date (anchor date for the curve). This is the reference date from which all time calculations are measured.',
            'dates': 'List of dates for curve points (tenors). These represent the maturities of the zero-coupon bonds whose yields form the curve.',
            'rates': 'List of zero rates corresponding to the dates. These are the annualized yields of zero-coupon bonds maturing on the specified dates.',
            'day_count_convention': 'Method for calculating year fractions. Determines how the time between two dates is measured in years.',
            'compounding_basis': 'Compounding frequency for the rates (e.g., Continuous, Annual, Semi-Annual). Affects how interest accrues over time.'
        },
        example: {
            base_date: { year: 2025, month: 5, day: 5 },
            dates: [
                { year: 2025, month: 11, day: 5 },
                { year: 2026, month: 5, day: 5 },
                { year: 2027, month: 5, day: 5 },
                { year: 2030, month: 5, day: 5 }
            ],
            rates: [0.03, 0.035, 0.04, 0.045],
            day_count_convention: 'ACT_365F',
            compounding_basis: 1
        },
        schema: {
            type: 'object',
            properties: {
                base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                dates: { 
                    type: 'array', 
                    items: { 
                        type: 'object', 
                        properties: { 
                            year: { type: 'integer' }, 
                            month: { type: 'integer' }, 
                            day: { type: 'integer' } 
                        } 
                    } 
                },
                rates: { type: 'array', items: { type: 'number' } },
                day_count_convention: { 
                    type: 'string', 
                    enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                },
                compounding_basis: { 
                    type: 'integer',
                    enum: [0, 1, 2, 3, 4],
                    enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                }
            }
        }
    },
    'discount-factor': {
        title: 'Get Discount Factor',
        endpoint: '/api/discount-factor',
        method: 'POST',
        description: `
            <p>Calculates a discount factor for a specific date based on a zero curve. Discount factors represent
            the present value of a unit payment in the future and are essential for pricing financial instruments.</p>
            
            <h4>Underlying Logic</h4>
            <p>The discount factor calculation applies the core time value of money concept:</p>
            <ul>
                <li>First, the API identifies the surrounding curve points that bracket the target date</li>
                <li>It then applies the chosen interpolation method between those points</li>
                <li>The interpolated rate is then converted to a discount factor using appropriate formulas</li>
                <li>For annual compounding: DF = 1 / (1 + r)^t where r is the rate and t is the year fraction</li>
                <li>For continuous compounding: DF = exp(-r*t)</li>
            </ul>
        `,
        fieldDescriptions: {
            'curve': 'The zero curve definition used for discounting. Contains dates, rates, and conventions.',
            'curve.base_date': 'The valuation date (anchor date for the curve).',
            'curve.dates': 'List of dates for curve points.',
            'curve.rates': 'List of zero rates corresponding to the dates.',
            'curve.day_count_convention': 'Method for calculating year fractions.',
            'curve.compounding_basis': 'Compounding frequency for the rates.',
            'target_date': 'The date for which to calculate the discount factor. This is when the future payment occurs.',
            'interpolation_method': 'Method to use for interpolation between curve points (Linear, Flat Forward, Linear Forward).'
        },
        example: {
            curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            target_date: { year: 2026, month: 1, day: 5 },
            interpolation_method: 2
        },
        schema: {
            type: 'object',
            properties: {
                curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                target_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                interpolation_method: { 
                    type: 'integer',
                    enum: [1, 2, 3],
                    enumLabels: ['Linear', 'Flat Forward', 'Linear Forward']
                }
            }
        }
    },
    'zero-rate': {
        title: 'Get Zero Rate',
        endpoint: '/api/zero-rate',
        method: 'POST',
        description: `
            <p>Calculates a zero rate for a specific date based on a zero curve. Zero rates represent
            the yield of a zero-coupon bond with a given maturity date.</p>
            
            <h4>Underlying Logic</h4>
            <p>The zero rate calculation follows these steps:</p>
            <ul>
                <li>First, a discount factor is obtained for the target date using the interpolation method specified</li>
                <li>This discount factor represents the present value of 1 unit paid at the target date</li>
                <li>The discount factor is then converted back to a zero rate using appropriate formulas</li>
                <li>For annual compounding: r = (1/DF)^(1/t) - 1 where DF is the discount factor and t is the time</li>
                <li>For continuous compounding: r = -ln(DF)/t</li>
            </ul>
        `,
        fieldDescriptions: {
            'curve': 'The zero curve definition used for calculation. Contains dates, rates, and conventions.',
            'curve.base_date': 'The valuation date (anchor date for the curve).',
            'curve.dates': 'List of dates for curve points.',
            'curve.rates': 'List of zero rates corresponding to the dates.',
            'curve.day_count_convention': 'Method for calculating year fractions.',
            'curve.compounding_basis': 'Compounding frequency for the rates.',
            'target_date': 'The date for which to calculate the zero rate. This represents the maturity of a hypothetical zero-coupon bond.',
            'interpolation_method': 'Method to use for interpolation between curve points (Linear, Flat Forward, Linear Forward).'
        },
        example: {
            curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            target_date: { year: 2028, month: 5, day: 5 },
            interpolation_method: 2
        },
        schema: {
            type: 'object',
            properties: {
                curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                target_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                interpolation_method: { 
                    type: 'integer',
                    enum: [1, 2, 3],
                    enumLabels: ['Linear', 'Flat Forward', 'Linear Forward']
                }
            }
        }
    },
    'forward-rate': {
        title: 'Get Forward Rate',
        endpoint: '/api/forward-rate',
        method: 'POST',
        description: `
            <p>Calculates a forward rate between two dates based on a zero curve. Forward rates represent
            the implied interest rate between two future dates.</p>
            
            <h4>Underlying Logic</h4>
            <p>The forward rate calculation follows this approach:</p>
            <ul>
                <li>Get discount factors for both the start date (DF₁) and end date (DF₂) using curve interpolation</li>
                <li>Calculate the forward discount factor as the ratio: FDF = DF₂/DF₁</li>
                <li>This represents the discount factor for the period between start date and end date</li>
                <li>Convert this forward discount factor to a rate using appropriate formulas</li>
                <li>For annual compounding: r = (1/FDF)^(1/t) - 1 where t is the period length</li>
                <li>For continuous compounding: r = -ln(FDF)/t</li>
            </ul>
        `,
        fieldDescriptions: {
            'curve': 'The zero curve definition used for calculation. Contains dates, rates, and conventions.',
            'curve.base_date': 'The valuation date (anchor date for the curve).',
            'curve.dates': 'List of dates for curve points.',
            'curve.rates': 'List of zero rates corresponding to the dates.',
            'curve.day_count_convention': 'Method for calculating year fractions.',
            'curve.compounding_basis': 'Compounding frequency for the rates.',
            'start_date': 'The start date of the forward period. This is when the forward rate would begin.',
            'end_date': 'The end date of the forward period. This is when the forward rate would end.',
            'interpolation_method': 'Method to use for interpolation between curve points (Linear, Flat Forward, Linear Forward).'
        },
        example: {
            curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            start_date: { year: 2026, month: 5, day: 5 },
            end_date: { year: 2027, month: 5, day: 5 },
            interpolation_method: 2
        },
        schema: {
            type: 'object',
            properties: {
                curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                start_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                end_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                interpolation_method: { 
                    type: 'integer',
                    enum: [1, 2, 3],
                    enumLabels: ['Linear', 'Flat Forward', 'Linear Forward']
                }
            }
        }
    },
    'bootstrap-credit-curve': {
        title: 'Bootstrap Credit Curve',
        endpoint: '/api/bootstrap-credit-curve',
        method: 'POST',
        description: `
            <p>Bootstraps a credit curve (survival probability curve) from market CDS spreads. This curve
            represents the market-implied probability of default over time and is essential for pricing CDS.</p>
            
            <h4>Underlying Logic</h4>
            <p>The credit curve bootstrapping process uses this approach:</p>
            <ul>
                <li>Start with a flat hazard rate of zero at valuation date (100% survival probability)</li>
                <li>For each CDS tenor/spread pair, working from shortest to longest:</li>
                <li>Calculate the implied hazard rate that makes the CDS price to par at the given spread</li>
                <li>This involves solving for the hazard rate that makes premium leg PV = protection leg PV</li>
                <li>Add this point to the survival curve</li>
                <li>The hazard rate (h) represents the instantaneous probability of default</li>
                <li>Survival probability (S) relates to hazard rate through: S(t) = exp(-h*t) in the constant hazard rate model</li>
            </ul>
        `,
        fieldDescriptions: {
            'discount_curve': 'The interest rate curve for discounting cash flows. Contains dates, rates, and conventions.',
            'discount_curve.base_date': 'The valuation date (anchor date for the curve).',
            'discount_curve.dates': 'List of dates for curve points.',
            'discount_curve.rates': 'List of zero rates corresponding to the dates.',
            'discount_curve.day_count_convention': 'Method for calculating year fractions.',
            'discount_curve.compounding_basis': 'Compounding frequency for the rates.',
            'valuation_date': 'The valuation date for the bootstrapping process. Starting point for all calculations.',
            'cds_tenors_spreads': 'List of CDS tenors and spreads (market quotes). These are the inputs used to create the credit curve.',
            'cds_tenors_spreads.tenor_years': 'The tenor of the CDS contract in years (e.g., 1.0, 3.0, 5.0).',
            'cds_tenors_spreads.spread': 'The market spread of the CDS contract as a decimal (e.g., 0.01 for 100 bps).',
            'recovery_rate': 'The recovery rate assumption (typically 0.4 or 40%). This is the expected percentage of notional recovered in case of default.',
            'cds_convention': 'The day count convention for CDS contracts. Determines how premium payments are calculated.'
        },
        example: {
            discount_curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            valuation_date: { year: 2025, month: 5, day: 5 },
            cds_tenors_spreads: [
                { tenor_years: 1.0, spread: 0.01 },
                { tenor_years: 2.0, spread: 0.015 },
                { tenor_years: 3.0, spread: 0.018 },
                { tenor_years: 5.0, spread: 0.02 }
            ],
            recovery_rate: 0.4,
            cds_convention: 'ACT_360'
        },
        schema: {
            type: 'object',
            properties: {
                discount_curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                valuation_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                cds_tenors_spreads: {
                    type: 'array',
                    items: {
                        type: 'object',
                        properties: {
                            tenor_years: { type: 'number' },
                            spread: { type: 'number' }
                        }
                    }
                },
                recovery_rate: { type: 'number' },
                cds_convention: { 
                    type: 'string', 
                    enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                }
            }
        }
    },
    'price-cds': {
        title: 'Price CDS',
        endpoint: '/api/price-cds',
        method: 'POST',
        description: `
            <p>Prices a Credit Default Swap (CDS) contract according to the ISDA CDS Standard Model methodology.
            This calculates the present value of both the premium and protection legs, as well as other metrics.</p>
            
            <h4>Underlying Logic</h4>
            <p>The CDS pricing follows the ISDA CDS Standard Model methodology:</p>
            <ul>
                <li><strong>Premium Leg Valuation</strong>: Sum of all future premium payments</li>
                <li>Generate a schedule of premium payment dates based on the contract frequency</li>
                <li>For each payment date, calculate the survival probability, discount factor, and premium amount</li>
                <li>Sum the PV of all payments: premium × discount factor × survival probability</li>
                <li><strong>Protection Leg Valuation</strong>: Expected value of the contingent default payment</li>
                <li>Calculate the probability of default during each period using survival probabilities</li>
                <li>Calculate the loss given default: notional × (1 - recovery rate)</li>
                <li>Sum the PV of all protection payments: LGD × default probability × discount factor</li>
                <li><strong>Par Spread Calculation</strong>: The spread that makes the premium leg PV equal to the protection leg PV</li>
            </ul>
        `,
        fieldDescriptions: {
            'discount_curve': 'The interest rate curve for discounting cash flows. Contains dates, rates, and conventions.',
            'discount_curve.base_date': 'The valuation date (anchor date for the curve).',
            'discount_curve.dates': 'List of dates for curve points.',
            'discount_curve.rates': 'List of zero rates corresponding to the dates.',
            'discount_curve.day_count_convention': 'Method for calculating year fractions.',
            'discount_curve.compounding_basis': 'Compounding frequency for the rates.',
            'survival_curve': 'The survival probability curve (credit curve). Contains dates and hazard rates.',
            'survival_curve.base_date': 'The valuation date (anchor date for the curve).',
            'survival_curve.dates': 'List of dates for curve points.',
            'survival_curve.rates': 'List of hazard rates corresponding to the dates.',
            'survival_curve.day_count_convention': 'Method for calculating year fractions.',
            'survival_curve.compounding_basis': 'Compounding frequency for the rates.',
            'cds_contract': 'The CDS contract specification including dates, coupon info, and recovery rate.',
            'cds_contract.dates': 'Key dates for the CDS contract (trade date, effective date, etc.).',
            'cds_contract.dates.trade_date': 'The date on which the CDS trade is agreed.',
            'cds_contract.dates.effective_date': 'The date from which protection becomes effective.',
            'cds_contract.dates.maturity_date': 'The date on which the CDS contract expires.',
            'cds_contract.dates.value_date': 'The date on which the CDS is valued.',
            'cds_contract.dates.settlement_date': 'The date on which the initial payment (if any) is settled.',
            'cds_contract.dates.step_in_date': 'The date on which the protection seller steps in if default occurs.',
            'cds_contract.coupon_info': 'Information about the coupon payments.',
            'cds_contract.coupon_info.payment_frequency': 'Frequency of premium payments per year (e.g., 4 for quarterly).',
            'cds_contract.coupon_info.day_count_convention': 'Method for calculating premium payment amounts.',
            'cds_contract.coupon_info.business_day_convention': 'Method for adjusting payment dates that fall on non-business days.',
            'cds_contract.coupon_info.coupon_rate': 'The annualized premium rate as a decimal (e.g., 0.01 for 100 bps).',
            'cds_contract.notional': 'The notional amount of the CDS contract. This is the principal amount protected.',
            'cds_contract.recovery_rate': 'The assumed recovery rate in case of default as a decimal (e.g., 0.4 for 40%).',
            'cds_contract.include_accrued_premium': 'Whether to include accrued premium in the valuation (typically true).',
            'cds_contract.is_buy_protection': 'Whether the position is buying protection (true) or selling protection (false).'
        },
        example: {
            discount_curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            survival_curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 5, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2028, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.0, 0.01, 0.015, 0.018, 0.02],
                day_count_convention: 'ACT_365F',
                compounding_basis: 0
            },
            cds_contract: {
                dates: {
                    trade_date: { year: 2025, month: 5, day: 5 },
                    effective_date: { year: 2025, month: 5, day: 7 },
                    maturity_date: { year: 2030, month: 5, day: 7 },
                    value_date: { year: 2025, month: 5, day: 7 },
                    settlement_date: { year: 2025, month: 5, day: 9 },
                    step_in_date: { year: 2025, month: 5, day: 8 }
                },
                coupon_info: {
                    payment_frequency: 4,
                    day_count_convention: 'ACT_360',
                    business_day_convention: 'MODIFIED_FOLLOW',
                    coupon_rate: 0.01
                },
                notional: 10000000.0,
                recovery_rate: 0.4,
                include_accrued_premium: true,
                is_buy_protection: true
            }
        },
        schema: {
            type: 'object',
            properties: {
                discount_curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                survival_curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                cds_contract: {
                    type: 'object',
                    properties: {
                        dates: {
                            type: 'object',
                            properties: {
                                trade_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                effective_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                maturity_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                value_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                settlement_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                step_in_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } }
                            }
                        },
                        coupon_info: {
                            type: 'object',
                            properties: {
                                payment_frequency: { 
                                    type: 'integer',
                                    enum: [1, 2, 4, 12],
                                    enumLabels: ['Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                                },
                                day_count_convention: { 
                                    type: 'string', 
                                    enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                                },
                                business_day_convention: { 
                                    type: 'string', 
                                    enum: ['FOLLOW', 'MODIFIED_FOLLOW', 'PRECEDING', 'NONE'] 
                                },
                                coupon_rate: { type: 'number' }
                            }
                        },
                        notional: { type: 'number' },
                        recovery_rate: { type: 'number' },
                        include_accrued_premium: { type: 'boolean' },
                        is_buy_protection: { type: 'boolean' }
                    }
                }
            }
        }
    },
    'calculate-upfront': {
        title: 'Calculate Upfront Charge',
        endpoint: '/api/calculate-upfront',
        method: 'POST',
        description: `
            <p>Calculates the upfront charge (or payment) for a CDS contract. This is the amount that
            needs to be paid at the start of the contract to make it fair given the market conditions.</p>
            
            <h4>Underlying Logic</h4>
            <p>The upfront charge calculation follows the post-2009 "CDS Big Bang" market convention:</p>
            <ul>
                <li>Calculate the present value of both legs of the CDS</li>
                <li>Premium leg PV: Expected value of all future premium payments</li>
                <li>Protection leg PV: Expected value of the contingent default payment</li>
                <li>The upfront charge is the difference: Upfront = Protection leg PV - Premium leg PV</li>
                <li>Positive value: Protection buyer pays upfront to protection seller</li>
                <li>Negative value: Protection seller pays upfront to protection buyer</li>
                <li>The amount depends on the difference between the contractual coupon rate and the par spread</li>
            </ul>
        `,
        fieldDescriptions: {
            'discount_curve': 'The interest rate curve for discounting cash flows. Contains dates, rates, and conventions.',
            'discount_curve.base_date': 'The valuation date (anchor date for the curve).',
            'discount_curve.dates': 'List of dates for curve points.',
            'discount_curve.rates': 'List of zero rates corresponding to the dates.',
            'discount_curve.day_count_convention': 'Method for calculating year fractions.',
            'discount_curve.compounding_basis': 'Compounding frequency for the rates.',
            'survival_curve': 'The survival probability curve (credit curve). Contains dates and hazard rates.',
            'survival_curve.base_date': 'The valuation date (anchor date for the curve).',
            'survival_curve.dates': 'List of dates for curve points.',
            'survival_curve.rates': 'List of hazard rates corresponding to the dates.',
            'survival_curve.day_count_convention': 'Method for calculating year fractions.',
            'survival_curve.compounding_basis': 'Compounding frequency for the rates.',
            'cds_contract': 'The CDS contract specification including dates, coupon info, and recovery rate.',
            'cds_contract.dates': 'Key dates for the CDS contract (trade date, effective date, etc.).',
            'cds_contract.dates.trade_date': 'The date on which the CDS trade is agreed.',
            'cds_contract.dates.effective_date': 'The date from which protection becomes effective.',
            'cds_contract.dates.maturity_date': 'The date on which the CDS contract expires.',
            'cds_contract.dates.value_date': 'The date on which the CDS is valued.',
            'cds_contract.dates.settlement_date': 'The date on which the initial payment (if any) is settled.',
            'cds_contract.dates.step_in_date': 'The date on which the protection seller steps in if default occurs.',
            'cds_contract.coupon_info': 'Information about the coupon payments.',
            'cds_contract.coupon_info.payment_frequency': 'Frequency of premium payments per year (e.g., 4 for quarterly).',
            'cds_contract.coupon_info.day_count_convention': 'Method for calculating premium payment amounts.',
            'cds_contract.coupon_info.business_day_convention': 'Method for adjusting payment dates that fall on non-business days.',
            'cds_contract.coupon_info.coupon_rate': 'The annualized premium rate as a decimal (e.g., 0.01 for 100 bps).',
            'cds_contract.notional': 'The notional amount of the CDS contract. This is the principal amount protected.',
            'cds_contract.recovery_rate': 'The assumed recovery rate in case of default as a decimal (e.g., 0.4 for 40%).',
            'cds_contract.include_accrued_premium': 'Whether to include accrued premium in the valuation (typically true).',
            'cds_contract.is_buy_protection': 'Whether the position is buying protection (true) or selling protection (false).'
        },
        example: {
            discount_curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 11, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.03, 0.035, 0.04, 0.045],
                day_count_convention: 'ACT_365F',
                compounding_basis: 1
            },
            survival_curve: {
                base_date: { year: 2025, month: 5, day: 5 },
                dates: [
                    { year: 2025, month: 5, day: 5 },
                    { year: 2026, month: 5, day: 5 },
                    { year: 2027, month: 5, day: 5 },
                    { year: 2028, month: 5, day: 5 },
                    { year: 2030, month: 5, day: 5 }
                ],
                rates: [0.0, 0.01, 0.015, 0.018, 0.02],
                day_count_convention: 'ACT_365F',
                compounding_basis: 0
            },
            cds_contract: {
                dates: {
                    trade_date: { year: 2025, month: 5, day: 5 },
                    effective_date: { year: 2025, month: 5, day: 7 },
                    maturity_date: { year: 2030, month: 5, day: 7 },
                    value_date: { year: 2025, month: 5, day: 7 },
                    settlement_date: { year: 2025, month: 5, day: 9 },
                    step_in_date: { year: 2025, month: 5, day: 8 }
                },
                coupon_info: {
                    payment_frequency: 4,
                    day_count_convention: 'ACT_360',
                    business_day_convention: 'MODIFIED_FOLLOW',
                    coupon_rate: 0.05
                },
                notional: 10000000.0,
                recovery_rate: 0.4,
                include_accrued_premium: true,
                is_buy_protection: true
            }
        },
        schema: {
            type: 'object',
            properties: {
                discount_curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                survival_curve: {
                    type: 'object',
                    properties: {
                        base_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                        dates: { 
                            type: 'array', 
                            items: { 
                                type: 'object', 
                                properties: { 
                                    year: { type: 'integer' }, 
                                    month: { type: 'integer' }, 
                                    day: { type: 'integer' } 
                                } 
                            } 
                        },
                        rates: { type: 'array', items: { type: 'number' } },
                        day_count_convention: { 
                            type: 'string', 
                            enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                        },
                        compounding_basis: { 
                            type: 'integer',
                            enum: [0, 1, 2, 3, 4],
                            enumLabels: ['Continuous', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                        }
                    }
                },
                cds_contract: {
                    type: 'object',
                    properties: {
                        dates: {
                            type: 'object',
                            properties: {
                                trade_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                effective_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                maturity_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                value_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                settlement_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } },
                                step_in_date: { type: 'object', properties: { year: { type: 'integer' }, month: { type: 'integer' }, day: { type: 'integer' } } }
                            }
                        },
                        coupon_info: {
                            type: 'object',
                            properties: {
                                payment_frequency: { 
                                    type: 'integer',
                                    enum: [1, 2, 4, 12],
                                    enumLabels: ['Annual', 'Semi-Annual', 'Quarterly', 'Monthly']
                                },
                                day_count_convention: { 
                                    type: 'string', 
                                    enum: ['ACT_365F', 'ACT_360', 'THIRTY_360', 'ACT_ACT_ISDA'] 
                                },
                                business_day_convention: { 
                                    type: 'string', 
                                    enum: ['FOLLOW', 'MODIFIED_FOLLOW', 'PRECEDING', 'NONE'] 
                                },
                                coupon_rate: { type: 'number' }
                            }
                        },
                        notional: { type: 'number' },
                        recovery_rate: { type: 'number' },
                        include_accrued_premium: { type: 'boolean' },
                        is_buy_protection: { type: 'boolean' }
                    }
                }
            }
        }
    }
};

// Global variables
let currentEndpoint = 'zero-curve';
let requestData = {};
let timeoutId = null;

// DOM Elements
const endpointList = document.querySelector('.endpoint-list');
const endpointTitle = document.getElementById('endpoint-title');
const formContainer = document.getElementById('form-container');
const requestJson = document.getElementById('request-json');
const responseJson = document.getElementById('response-json');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const loadExampleBtn = document.getElementById('load-example');
const clearFormBtn = document.getElementById('clear-form');
const updateFormBtn = document.getElementById('update-form');
const submitRequestBtn = document.getElementById('submit-request');
const documentationContent = document.getElementById('endpoint-documentation');

// Initialize the UI
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadEndpoint('zero-curve');
});

// Initialize event listeners
function initEventListeners() {
    // Endpoint selection
    endpointList.addEventListener('click', (e) => {
        if (e.target.tagName === 'LI') {
            const endpoint = e.target.dataset.endpoint;
            if (endpoint && endpoint !== currentEndpoint) {
                loadEndpoint(endpoint);
            }
        }
    });

    // Load example data
    loadExampleBtn.addEventListener('click', () => {
        loadExampleData();
    });

    // Clear form
    clearFormBtn.addEventListener('click', () => {
        clearForm();
    });

    // Update form from JSON
    updateFormBtn.addEventListener('click', () => {
        updateFormFromJson();
    });

    // Submit request
    submitRequestBtn.addEventListener('click', () => {
        submitRequest();
    });

    // Automatically update JSON when form values change
    formContainer.addEventListener('change', (e) => {
        if (e.target.classList.contains('form-control')) {
            updateJsonFromForm();
        }
    });

    // Debounce JSON editor updates
    requestJson.addEventListener('input', () => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            try {
                const json = JSON.parse(requestJson.textContent);
                formatJsonEditor(requestJson, json);
                requestData = json;
            } catch (error) {
                // Invalid JSON, don't update
            }
        }, 500);
    });
}

// Load an endpoint and show its form
function loadEndpoint(endpoint) {
    // Update active state in sidebar
    document.querySelectorAll('.endpoint-list li').forEach(li => {
        li.classList.remove('active');
    });
    document.querySelector(`[data-endpoint="${endpoint}"]`).classList.add('active');

    // Update title
    currentEndpoint = endpoint;
    endpointTitle.textContent = apiEndpoints[endpoint].title;

    // Clear response
    responseJson.innerHTML = '';
    statusIndicator.className = 'status-indicator';
    statusText.textContent = 'Status: Ready';

    // Update documentation
    updateDocumentation(endpoint);

    // Generate form and load example data
    generateForm(apiEndpoints[endpoint].schema);
    loadExampleData();
}

// Update the documentation section with endpoint description and field info
function updateDocumentation(endpoint) {
    const endpointData = apiEndpoints[endpoint];
    
    // Generate HTML content for documentation
    let html = endpointData.description || '';
    
    // Add field descriptions
    if (endpointData.fieldDescriptions) {
        html += `
            <div class="field-descriptions">
                <h4>Field Descriptions</h4>
                <dl>
        `;
        
        for (const [field, description] of Object.entries(endpointData.fieldDescriptions)) {
            html += `
                <dt>${formatKeyForDisplay(field)}</dt>
                <dd>${description}</dd>
            `;
        }
        
        html += `
                </dl>
            </div>
        `;
    }
    
    documentationContent.innerHTML = html;
}

// Generate a form from a JSON schema
function generateForm(schema, parentKey = '', level = 0) {
    if (level === 0) {
        formContainer.innerHTML = '';
    }

    if (!schema || schema.type !== 'object') {
        return;
    }

    const properties = schema.properties || {};

    for (const [key, prop] of Object.entries(properties)) {
        const fieldName = parentKey ? `${parentKey}.${key}` : key;
        
        if (prop.type === 'object') {
            // For objects, create a fieldset
            const fieldset = document.createElement('fieldset');
            fieldset.className = 'form-group object-group';
            fieldset.innerHTML = `<legend>${formatKeyForDisplay(key)}</legend>`;
            formContainer.appendChild(fieldset);
            
            // Recursively generate form for nested object
            generateForm(prop, fieldName, level + 1);
        } else if (prop.type === 'array') {
            // For arrays, create an array group container
            const arrayGroup = document.createElement('div');
            arrayGroup.className = 'array-group';
            arrayGroup.dataset.field = fieldName;
            arrayGroup.innerHTML = `
                <h4>${formatKeyForDisplay(key)}</h4>
                <div class="array-items" id="${fieldName}-items"></div>
                <div class="array-controls">
                    <button class="action-button add-item-btn" data-field="${fieldName}">Add Item</button>
                </div>
            `;
            formContainer.appendChild(arrayGroup);
            
            // Add handler for adding new items
            arrayGroup.querySelector('.add-item-btn').addEventListener('click', () => {
                addArrayItem(fieldName, prop.items);
            });
        } else {
            // For primitive types, create input fields
            createInputField(key, prop, fieldName);
        }
    }

    // Add event listeners after form generation
    if (level === 0) {
        addArrayItemEventListeners();
    }
}

// Create an input field based on property type
function createInputField(key, prop, fieldName) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    
    // Get the field description if available
    const description = getFieldDescription(fieldName);
    
    // Create label with help icon if there's a description
    const labelHtml = description ? 
        `<label for="${fieldName}">
            ${formatKeyForDisplay(key)}
            <span class="field-help-icon" title="Click for more info">?</span>
        </label>
        <div class="field-tooltip">${description}</div>` : 
        `<label for="${fieldName}">${formatKeyForDisplay(key)}</label>`;
    
    formGroup.innerHTML = labelHtml;
    
    let input;
    
    if (prop.enum) {
        // Create a select for enum values
        input = document.createElement('select');
        input.className = 'form-control';
        input.id = fieldName;
        input.name = fieldName;
        input.dataset.path = fieldName;
        
        prop.enum.forEach((value, index) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = prop.enumLabels && prop.enumLabels[index] ? `${prop.enumLabels[index]} (${value})` : value;
            input.appendChild(option);
        });
    } else if (prop.type === 'boolean') {
        // Create a select for boolean values
        input = document.createElement('select');
        input.className = 'form-control';
        input.id = fieldName;
        input.name = fieldName;
        input.dataset.path = fieldName;
        
        const optionTrue = document.createElement('option');
        optionTrue.value = 'true';
        optionTrue.textContent = 'True';
        input.appendChild(optionTrue);
        
        const optionFalse = document.createElement('option');
        optionFalse.value = 'false';
        optionFalse.textContent = 'False';
        input.appendChild(optionFalse);
    } else if (fieldName.endsWith('.year') || fieldName.endsWith('.month') || fieldName.endsWith('.day')) {
        // For date components, create a number input with appropriate ranges
        input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control';
        input.id = fieldName;
        input.name = fieldName;
        input.dataset.path = fieldName;
        
        if (fieldName.endsWith('.year')) {
            input.min = 2000;
            input.max = 2100;
            input.value = 2025;
        } else if (fieldName.endsWith('.month')) {
            input.min = 1;
            input.max = 12;
            input.value = 1;
        } else if (fieldName.endsWith('.day')) {
            input.min = 1;
            input.max = 31;
            input.value = 1;
        }
    } else if (prop.type === 'number' || prop.type === 'integer') {
        // For numbers, create a number input
        input = document.createElement('input');
        input.type = 'number';
        input.step = prop.type === 'integer' ? '1' : 'any';
        input.className = 'form-control';
        input.id = fieldName;
        input.name = fieldName;
        input.dataset.path = fieldName;
    } else {
        // Default to text input
        input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control';
        input.id = fieldName;
        input.name = fieldName;
        input.dataset.path = fieldName;
    }
    
    formGroup.appendChild(input);
    formContainer.appendChild(formGroup);
}

// Get description for a specific field
function getFieldDescription(fieldPath) {
    const fieldDescriptions = apiEndpoints[currentEndpoint].fieldDescriptions;
    if (!fieldDescriptions) return null;
    
    // Try exact match first
    if (fieldDescriptions[fieldPath]) {
        return fieldDescriptions[fieldPath];
    }
    
    // For nested paths, try to find partial matches
    if (fieldPath.includes('.')) {
        // Check if any field description partially matches the path
        for (const [key, description] of Object.entries(fieldDescriptions)) {
            if (fieldPath.includes(key)) {
                return description;
            }
        }
    }
    
    return null;
}

// Add a new item to an array
function addArrayItem(fieldName, itemSchema) {
    const arrayItems = document.getElementById(`${fieldName}-items`);
    const itemIndex = arrayItems.children.length;
    const itemId = `${fieldName}[${itemIndex}]`;
    
    const arrayItem = document.createElement('div');
    arrayItem.className = 'array-item';
    arrayItem.dataset.index = itemIndex;
    
    // If the item is a simple value, add a single input
    if (itemSchema.type !== 'object') {
        arrayItem.innerHTML = `
            <div class="form-group">
                <label for="${itemId}">Item ${itemIndex + 1}</label>
                <div class="input-group">
                    <input type="${itemSchema.type === 'number' ? 'number' : 'text'}" 
                           class="form-control" 
                           id="${itemId}" 
                           name="${itemId}" 
                           data-path="${fieldName}[${itemIndex}]">
                    <button class="action-button remove-item-btn" data-field="${fieldName}" data-index="${itemIndex}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        arrayItems.appendChild(arrayItem);
    } else {
        // If the item is an object, add inputs for all properties
        arrayItem.innerHTML = `
            <div class="array-item-header">
                <h5>Item ${itemIndex + 1}</h5>
                <button class="action-button remove-item-btn" data-field="${fieldName}" data-index="${itemIndex}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        const itemForm = document.createElement('div');
        itemForm.className = 'array-item-form';
        arrayItem.appendChild(itemForm);
        arrayItems.appendChild(arrayItem);
        
        // Add fields for each property in the object
        if (itemSchema.properties) {
            for (const [propName, propSchema] of Object.entries(itemSchema.properties)) {
                const propPath = `${fieldName}[${itemIndex}].${propName}`;
                const propGroup = document.createElement('div');
                propGroup.className = 'form-group';
                propGroup.innerHTML = `<label for="${propPath}">${formatKeyForDisplay(propName)}</label>`;
                
                let propInput;
                
                if (propSchema.type === 'object') {
                    // For nested objects, recursively add form fields
                    const nestedForm = document.createElement('div');
                    nestedForm.className = 'nested-form';
                    propGroup.appendChild(nestedForm);
                    
                    for (const [nestedProp, nestedSchema] of Object.entries(propSchema.properties)) {
                        const nestedPath = `${propPath}.${nestedProp}`;
                        const nestedGroup = document.createElement('div');
                        nestedGroup.className = 'form-group';
                        nestedGroup.innerHTML = `<label for="${nestedPath}">${formatKeyForDisplay(nestedProp)}</label>`;
                        
                        const nestedInput = document.createElement('input');
                        nestedInput.type = nestedSchema.type === 'number' ? 'number' : 'text';
                        nestedInput.className = 'form-control';
                        nestedInput.id = nestedPath;
                        nestedInput.name = nestedPath;
                        nestedInput.dataset.path = nestedPath;
                        
                        nestedGroup.appendChild(nestedInput);
                        nestedForm.appendChild(nestedGroup);
                    }
                } else if (propSchema.enum) {
                    // For enums, create a select
                    propInput = document.createElement('select');
                    propInput.className = 'form-control';
                    propInput.id = propPath;
                    propInput.name = propPath;
                    propInput.dataset.path = propPath;
                    
                    propSchema.enum.forEach((value, index) => {
                        const option = document.createElement('option');
                        option.value = value;
                        option.textContent = propSchema.enumLabels && propSchema.enumLabels[index] ? `${propSchema.enumLabels[index]} (${value})` : value;
                        propInput.appendChild(option);
                    });
                    
                    propGroup.appendChild(propInput);
                } else {
                    // For basic types, create an input
                    propInput = document.createElement('input');
                    propInput.type = propSchema.type === 'number' ? 'number' : 'text';
                    propInput.className = 'form-control';
                    propInput.id = propPath;
                    propInput.name = propPath;
                    propInput.dataset.path = propPath;
                    
                    propGroup.appendChild(propInput);
                }
                
                itemForm.appendChild(propGroup);
            }
        }
    }
    
    // Update change event listeners
    arrayItem.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('change', updateJsonFromForm);
    });
    
    // Update remove buttons
    updateRemoveItemButtons();
}

// Add event listeners to array item controls
function addArrayItemEventListeners() {
    // Delegate events for array item removal
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-item-btn') || 
            e.target.parentElement.classList.contains('remove-item-btn')) {
            
            const button = e.target.classList.contains('remove-item-btn') ? 
                           e.target : e.target.parentElement;
            
            const field = button.dataset.field;
            const index = parseInt(button.dataset.index, 10);
            
            removeArrayItem(field, index);
        }
    });
}

// Remove an item from an array
function removeArrayItem(fieldName, index) {
    const arrayItems = document.getElementById(`${fieldName}-items`);
    const items = Array.from(arrayItems.children);
    
    // Remove the item at the specified index
    if (items[index]) {
        items[index].remove();
    }
    
    // Update indices for remaining items
    items.forEach((item, i) => {
        if (i > index) {
            // Update data attribute
            item.dataset.index = i - 1;
            
            // Update header
            const header = item.querySelector('h5') || item.querySelector('label');
            if (header) {
                header.textContent = header.textContent.replace(/Item \d+/, `Item ${i}`);
            }
            
            // Update input paths
            item.querySelectorAll('.form-control').forEach(input => {
                const path = input.dataset.path;
                const newPath = path.replace(/\[\d+\]/, `[${i - 1}]`);
                input.dataset.path = newPath;
                input.id = newPath;
                input.name = newPath;
            });
            
            // Update remove button
            const removeBtn = item.querySelector('.remove-item-btn');
            if (removeBtn) {
                removeBtn.dataset.index = i - 1;
            }
        }
    });
    
    // Update JSON
    updateJsonFromForm();
}

// Update remove item buttons
function updateRemoveItemButtons() {
    document.querySelectorAll('.remove-item-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const field = e.target.dataset.field;
            const index = parseInt(e.target.dataset.index, 10);
            removeArrayItem(field, index);
        });
    });
}

// Format a key for display (convert camelCase to Title Case with spaces)
function formatKeyForDisplay(key) {
    return key
        .replace(/([A-Z])/g, ' $1') // Add space before capital letters
        .replace(/_/g, ' ') // Replace underscores with spaces
        .replace(/^\w/, c => c.toUpperCase()) // Capitalize first letter
        .trim();
}

// Load example data for the current endpoint
function loadExampleData() {
    const example = apiEndpoints[currentEndpoint].example;
    requestData = JSON.parse(JSON.stringify(example)); // Deep copy
    
    // Update JSON editor
    formatJsonEditor(requestJson, requestData);
    
    // Update form values
    populateFormFromJson(requestData);
}

// Clear the form
function clearForm() {
    // Clear form inputs
    formContainer.querySelectorAll('.form-control').forEach(input => {
        if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        } else {
            input.value = '';
        }
    });
    
    // Clear array items
    formContainer.querySelectorAll('.array-items').forEach(container => {
        container.innerHTML = '';
    });
    
    // Clear JSON
    requestData = {};
    formatJsonEditor(requestJson, requestData);
    
    // Clear response
    responseJson.innerHTML = '';
    statusIndicator.className = 'status-indicator';
    statusText.textContent = 'Status: Ready';
}

// Update JSON from form values
function updateJsonFromForm() {
    const data = {};
    
    // Process all form controls
    formContainer.querySelectorAll('.form-control').forEach(input => {
        if (!input.dataset.path) return;
        
        const path = input.dataset.path;
        let value = input.value;
        
        // Convert values based on input type
        if (input.type === 'number') {
            value = value === '' ? null : Number(value);
        } else if (input.tagName === 'SELECT' && input.options[input.selectedIndex].value === 'true') {
            value = true;
        } else if (input.tagName === 'SELECT' && input.options[input.selectedIndex].value === 'false') {
            value = false;
        }
        
        // Skip empty values
        if (value === '' || value === null) return;
        
        // Set the value in the data object
        setNestedValue(data, path, value);
    });
    
    requestData = data;
    formatJsonEditor(requestJson, data);
}

// Update form from JSON
function updateFormFromJson() {
    try {
        const json = JSON.parse(requestJson.textContent);
        requestData = json;
        populateFormFromJson(json);
    } catch (error) {
        showError('Invalid JSON: ' + error.message);
    }
}

// Populate form with values from JSON
function populateFormFromJson(json) {
    // Clear array items first
    formContainer.querySelectorAll('.array-items').forEach(container => {
        container.innerHTML = '';
    });
    
    // Process the JSON recursively
    populateFormFields(json);
}

// Populate form fields with values from JSON
function populateFormFields(json, parentPath = '') {
    if (!json || typeof json !== 'object') return;
    
    if (Array.isArray(json)) {
        // Handle arrays
        const arrayField = parentPath;
        const arrayContainer = document.querySelector(`[data-field="${arrayField}"]`);
        
        if (arrayContainer) {
            const itemsSchema = apiEndpoints[currentEndpoint].schema;
            let itemSchema = getSchemaForPath(itemsSchema, arrayField + '[0]');
            
            // Add items for each array element
            json.forEach((item, index) => {
                // Add empty item to the form
                addArrayItem(arrayField, itemSchema);
                
                // If item is an object, populate its fields
                if (typeof item === 'object' && !Array.isArray(item)) {
                    for (const [key, value] of Object.entries(item)) {
                        const fieldPath = `${arrayField}[${index}].${key}`;
                        
                        if (typeof value === 'object' && !Array.isArray(value)) {
                            // Nested object inside array item
                            for (const [nestedKey, nestedValue] of Object.entries(value)) {
                                const nestedPath = `${fieldPath}.${nestedKey}`;
                                const input = document.querySelector(`[data-path="${nestedPath}"]`);
                                if (input) setInputValue(input, nestedValue);
                            }
                        } else {
                            // Simple value inside array item
                            const input = document.querySelector(`[data-path="${fieldPath}"]`);
                            if (input) setInputValue(input, value);
                        }
                    }
                } else {
                    // Simple array item
                    const fieldPath = `${arrayField}[${index}]`;
                    const input = document.querySelector(`[data-path="${fieldPath}"]`);
                    if (input) setInputValue(input, item);
                }
            });
        }
    } else {
        // Handle objects
        for (const [key, value] of Object.entries(json)) {
            const fieldPath = parentPath ? `${parentPath}.${key}` : key;
            
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                // Recursively populate nested objects
                populateFormFields(value, fieldPath);
            } else if (Array.isArray(value)) {
                // Handle nested arrays
                populateFormFields(value, fieldPath);
            } else {
                // Handle simple values
                const input = document.querySelector(`[data-path="${fieldPath}"]`);
                if (input) setInputValue(input, value);
            }
        }
    }
}

// Set input value based on type
function setInputValue(input, value) {
    if (input.tagName === 'SELECT') {
        // For select elements, find the option with matching value
        const option = Array.from(input.options).find(opt => opt.value == value);
        if (option) input.value = option.value;
    } else {
        // For other inputs, set the value directly
        input.value = value;
    }
}

// Get schema for a specific path
function getSchemaForPath(schema, path) {
    if (!schema || !path) return null;
    
    const parts = path.replace(/\[\d+\]/g, '[0]').split('.');
    let current = schema;
    
    for (const part of parts) {
        if (part.includes('[')) {
            // Handle array paths (e.g., "items[0]")
            const arrayName = part.split('[')[0];
            
            if (current.properties && current.properties[arrayName]) {
                current = current.properties[arrayName].items;
            } else {
                return null;
            }
        } else if (current.properties && current.properties[part]) {
            current = current.properties[part];
        } else {
            return null;
        }
    }
    
    return current;
}

// Submit the API request
async function submitRequest() {
    // Update status
    statusIndicator.className = 'status-indicator';
    statusText.textContent = 'Status: Processing...';
    
    try {
        const endpoint = apiEndpoints[currentEndpoint].endpoint;
        const method = apiEndpoints[currentEndpoint].method;
        
        const response = await fetch(endpoint, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        // Update status
        if (response.ok) {
            statusIndicator.className = 'status-indicator success';
            statusText.textContent = `Status: Success (${response.status})`;
        } else {
            statusIndicator.className = 'status-indicator error';
            statusText.textContent = `Status: Error (${response.status})`;
        }
        
        // Display response
        formatJsonEditor(responseJson, result);
    } catch (error) {
        statusIndicator.className = 'status-indicator error';
        statusText.textContent = `Status: Error (${error.message})`;
        responseJson.textContent = `Error: ${error.message}`;
    }
}

// Set a nested value in an object using a path
function setNestedValue(obj, path, value) {
    const parts = path.split('.');
    
    for (let i = 0; i < parts.length; i++) {
        let part = parts[i];
        const arrayMatch = part.match(/^([^\[]+)\[(\d+)\]$/);
        
        if (arrayMatch) {
            // Handle array paths (e.g., "items[0]")
            const arrayName = arrayMatch[1];
            const arrayIndex = parseInt(arrayMatch[2], 10);
            
            if (i === parts.length - 1) {
                // Last part, set the value
                if (!obj[arrayName]) obj[arrayName] = [];
                ensureArrayLength(obj[arrayName], arrayIndex + 1);
                obj[arrayName][arrayIndex] = value;
                return;
            } else {
                // Not the last part, ensure the next object exists
                if (!obj[arrayName]) obj[arrayName] = [];
                ensureArrayLength(obj[arrayName], arrayIndex + 1);
                if (!obj[arrayName][arrayIndex]) obj[arrayName][arrayIndex] = {};
                obj = obj[arrayName][arrayIndex];
            }
        } else {
            if (i === parts.length - 1) {
                // Last part, set the value
                obj[part] = value;
            } else {
                // Not the last part, ensure the next object exists
                if (!obj[part]) obj[part] = {};
                obj = obj[part];
            }
        }
    }
}

// Ensure an array has at least the specified length
function ensureArrayLength(arr, length) {
    while (arr.length < length) {
        arr.push(null);
    }
}

// Format JSON in the editor
function formatJsonEditor(editor, json) {
    editor.textContent = JSON.stringify(json, null, 2);
    
    // Apply syntax highlighting
    const content = editor.textContent;
    const highlighted = formatJsonSyntax(content);
    editor.innerHTML = highlighted;
}

// Format JSON syntax with highlighting
function formatJsonSyntax(json) {
    return json
        .replace(/"([^"]+)":/g, '<span class="syntax-key">"$1"</span>:')
        .replace(/: "(.*?)"/g, ': <span class="syntax-string">"$1"</span>')
        .replace(/: (\d+\.?\d*)/g, ': <span class="syntax-number">$1</span>')
        .replace(/: (true|false)/g, ': <span class="syntax-boolean">$1</span>')
        .replace(/: null/g, ': <span class="syntax-null">null</span>');
}

// Show an error message
function showError(message) {
    statusIndicator.className = 'status-indicator error';
    statusText.textContent = `Error: ${message}`;
}