import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Proof audit for “Cheap Attention, Costly Commitment”

This file machine-checks the algebraic and order-theoretic cores used in the
paper.  It deliberately does not claim a formalization of Brouwer's theorem or
the local saddle-node theorem; those results are invoked in their standard
analytic form in the manuscript.
-/

namespace CrossRouteMatching

/-- The dynamic payoff difference factors through the conversion cutoff. -/
theorem choice_gap_identity
    (δ L_H r L_A q γ S_H : ℝ)
    (h_cutoff : (1 + δ) * L_A =
      S_H + δ * (γ * L_H + (1 - γ) * r * L_A)) :
    S_H + δ * (q * L_H + (1 - q) * r * L_A) - (1 + δ) * L_A =
      δ * (L_H - r * L_A) * (q - γ) := by
  rw [h_cutoff]
  ring

/-- Below the calibrated cutoff, choosing the short-term route is costly. -/
theorem inefficient_delay_loss_positive
    (δ L_H r L_A q γ S_H : ℝ)
    (hδ : 0 < δ)
    (hspread : 0 < L_H - r * L_A)
    (hq : q < γ)
    (h_cutoff : (1 + δ) * L_A =
      S_H + δ * (γ * L_H + (1 - γ) * r * L_A)) :
    S_H + δ * (q * L_H + (1 - q) * r * L_A) < (1 + δ) * L_A := by
  have hcoef : 0 < δ * (L_H - r * L_A) := mul_pos hδ hspread
  have hdiff : q - γ < 0 := sub_neg.mpr hq
  have hgap : δ * (L_H - r * L_A) * (q - γ) < 0 :=
    mul_neg_of_pos_of_neg hcoef hdiff
  have hid := choice_gap_identity δ L_H r L_A q γ S_H h_cutoff
  linarith

/-- The paired Lipschitz inequalities imply uniqueness when slopes multiply
to less than one.  This is the scalar core of Proposition 3. -/
theorem two_sided_contraction_core
    (dx dy a b : ℝ)
    (ha : 0 ≤ a)
    (hab : a * b < 1)
    (hx : |dx| ≤ a * |dy|)
    (hy : |dy| ≤ b * |dx|) :
    dx = 0 ∧ dy = 0 := by
  have hcombo : |dx| ≤ (a * b) * |dx| := by
    calc
      |dx| ≤ a * |dy| := hx
      _ ≤ a * (b * |dx|) := mul_le_mul_of_nonneg_left hy ha
      _ = (a * b) * |dx| := by ring
  have hdx : dx = 0 := by
    by_contra hne
    have hpos : 0 < |dx| := abs_pos.mpr hne
    have hstrict : (a * b) * |dx| < 1 * |dx| :=
      mul_lt_mul_of_pos_right hab hpos
    linarith
  have hdy_abs : |dy| = 0 := by
    rw [hdx, abs_zero, mul_zero] at hy
    exact le_antisymm hy (abs_nonneg dy)
  exact ⟨hdx, abs_eq_zero.mp hdy_abs⟩

/-- If acceptance and participation weakly fall, and acceptance falls strictly,
successful volume falls strictly whenever initial participation is positive. -/
theorem match_volume_monotone
    (α₁ α₀ x₁ x₀ : ℝ)
    (hα₁ : 0 ≤ α₁)
    (hα : α₁ < α₀)
    (hx : x₁ ≤ x₀)
    (hx₀ : 0 < x₀) :
    α₁ * x₁ < α₀ * x₀ := by
  calc
    α₁ * x₁ ≤ α₁ * x₀ := mul_le_mul_of_nonneg_left hx hα₁
    _ < α₀ * x₀ := mul_lt_mul_of_pos_right hα hx₀

end CrossRouteMatching
