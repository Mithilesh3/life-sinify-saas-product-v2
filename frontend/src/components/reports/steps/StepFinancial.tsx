interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepFinancial({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const updateNumber = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      financial: {
        ...current.financial,
        [field]: value === "" ? "" : Number(value),
      },
    }));
  };

  const updateSelect = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      financial: {
        ...current.financial,
        [field]: value,
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title text-white">Financial Snapshot</h2>

      <input
        type="number"
        placeholder="Monthly Income"
        className="input"
        value={formData.financial.monthly_income ?? ""}
        onChange={(e) => updateNumber("monthly_income", e.target.value)}
      />

      <input
        type="number"
        min="0"
        max="100"
        placeholder="Savings Ratio (%)"
        className="input"
        value={formData.financial.savings_ratio ?? ""}
        onChange={(e) => updateNumber("savings_ratio", e.target.value)}
      />

      <input
        type="number"
        min="0"
        max="100"
        placeholder="Debt Ratio (%)"
        className="input"
        value={formData.financial.debt_ratio ?? ""}
        onChange={(e) => updateNumber("debt_ratio", e.target.value)}
      />

      <select
        className="input"
        value={formData.financial.risk_tolerance ?? ""}
        onChange={(e) => updateSelect("risk_tolerance", e.target.value)}
      >
        <option value="">Risk Tolerance</option>
        <option value="low">Low</option>
        <option value="moderate">Moderate</option>
        <option value="high">High</option>
      </select>

      <div className="flex justify-between">
        <button onClick={prev} className="btn-secondary">
          Back
        </button>
        <button onClick={next} className="btn-primary">
          Continue
        </button>
      </div>
    </div>
  );
}
