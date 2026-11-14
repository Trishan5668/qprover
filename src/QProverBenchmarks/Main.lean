import Mathlib

theorem add_zero_bench (n : Nat) : n + 0 = n := by simp
theorem zero_add_bench (n : Nat) : 0 + n = n := by simp
theorem mul_one_bench (n : Nat) : n * 1 = n := by simp
theorem one_mul_bench (n : Nat) : 1 * n = n := by simp
theorem sub_self_bench (n : Nat) : n - n = 0 := by simp
theorem and_true_bench (p : Prop) : p ∧ True ↔ p := by simp
theorem or_false_bench (p : Prop) : p ∨ False ↔ p := by simp
theorem not_false_bench : ¬ False := by simp
theorem eq_self_bench (n : Nat) : n = n := by rfl
theorem le_refl_bench (n : Nat) : n ≤ n := by omega
theorem zero_le_bench (n : Nat) : 0 ≤ n := by omega
theorem succ_pos_bench (n : Nat) : 0 < n + 1 := by omega
theorem add_assoc_bench (a b c : Nat) : a + b + c = a + (b + c) := by omega
theorem add_comm_bench (a b : Nat) : a + b = b + a := by omega
theorem mul_zero_bench (n : Nat) : n * 0 = 0 := by simp
theorem zero_mul_bench (n : Nat) : 0 * n = 0 := by simp
theorem pow_zero_bench (n : Nat) : n ^ 0 = 1 := by simp
theorem pow_one_bench (n : Nat) : n ^ 1 = n := by simp
theorem double_neg_bench (p : Prop) : ¬¬p ↔ p := by simp
theorem imp_true_bench (p : Prop) : p → True := by simp
theorem true_and_bench (p : Prop) : True ∧ p ↔ p := by simp
theorem false_or_bench (p : Prop) : False ∨ p ↔ p := by simp
theorem list_length_nil_bench : List.length ([] : List Nat) = 0 := by simp
theorem list_append_nil_bench (xs : List Nat) : [] ++ xs = xs := by simp
theorem list_reverse_nil_bench : ([].reverse : List Nat) = [] := by simp
theorem map_id_bench (xs : List Nat) : List.map id xs = xs := by simp
theorem filter_true_bench (xs : List Nat) : List.filter (fun _ : Nat => True) xs = xs := by simp
theorem nat_cast_zero_bench : (0 : Int) = 0 := by rfl
theorem nat_cast_one_bench : (1 : Int) = 1 := by rfl
theorem abs_zero_bench : Int.natAbs 0 = 0 := by rfl
theorem min_self_bench (n : Nat) : min n n = n := by simp
theorem max_self_bench (n : Nat) : max n n = n := by simp
theorem div_one_bench (n : Nat) : n / 1 = n := by simp
theorem mod_one_bench (n : Nat) : n % 1 = 0 := by simp
theorem finite_empty_bench : Set.Finite (∅ : Set Nat) := by simp
