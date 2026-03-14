interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepEmotional({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const update = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      emotional: {
        ...current.emotional,
        [field]: value === "" ? "" : Number(value),
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title text-white">Emotional State</h2>

      <input
        type="number"
        min="1"
        max="10"
        placeholder="Anxiety Level (1-10)"
        className="input"
        value={formData.emotional.anxiety_level ?? ""}
        onChange={(e) => update("anxiety_level", e.target.value)}
      />

      <input
        type="number"
        min="1"
        max="10"
        placeholder="Decision Confusion (1-10)"
        className="input"
        value={formData.emotional.decision_confusion ?? ""}
        onChange={(e) => update("decision_confusion", e.target.value)}
      />

      <input
        type="number"
        min="1"
        max="10"
        placeholder="Impulse Control (1-10)"
        className="input"
        value={formData.emotional.impulse_control ?? ""}
        onChange={(e) => update("impulse_control", e.target.value)}
      />

      <input
        type="number"
        min="1"
        max="10"
        placeholder="Emotional Stability (1-10)"
        className="input"
        value={formData.emotional.emotional_stability ?? ""}
        onChange={(e) => update("emotional_stability", e.target.value)}
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
