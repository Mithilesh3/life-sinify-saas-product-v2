interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepBusiness({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const update = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      business_history: {
        ...current.business_history,
        [field]: value === "" ? "" : Number(value),
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title mb-2 text-white">Business History</h2>

      <input
        type="number"
        placeholder="Major Investments"
        className="input"
        value={formData.business_history.major_investments ?? ""}
        onChange={(e) => update("major_investments", e.target.value)}
      />

      <input
        type="number"
        placeholder="Major Losses"
        className="input"
        value={formData.business_history.major_losses ?? ""}
        onChange={(e) => update("major_losses", e.target.value)}
      />

      <input
        type="number"
        placeholder="Risk Mistakes Count"
        className="input"
        value={formData.business_history.risk_mistakes_count ?? ""}
        onChange={(e) => update("risk_mistakes_count", e.target.value)}
      />

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
