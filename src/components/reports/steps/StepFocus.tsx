interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

const focusOptions = [
  { value: "career_growth", label: "Career Growth" },
  { value: "finance_debt", label: "Finance or Debt" },
  { value: "relationship", label: "Relationship" },
  { value: "health_stability", label: "Health Stability" },
  { value: "emotional_confusion", label: "Emotional Confusion" },
  { value: "business_decision", label: "Business Decision" },
  { value: "general_alignment", label: "General Alignment" },
];

export default function StepFocus({ formData, setFormData, next, prev }: Props) {
  const update = (value: string) => {
    setFormData((current: any) => ({
      ...current,
      focus: { life_focus: value },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title text-white">Primary Focus</h2>

      <select
        className="input"
        value={formData.focus.life_focus ?? ""}
        onChange={(e) => update(e.target.value)}
      >
        <option value="">Select</option>
        {focusOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
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
