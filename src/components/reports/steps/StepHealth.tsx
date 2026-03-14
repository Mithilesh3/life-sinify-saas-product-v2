interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepHealth({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const update = (field: string, value: string | number) => {
    setFormData((current: any) => ({
      ...current,
      health: {
        ...current.health,
        [field]: value,
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title mb-2 text-white">Health Profile</h2>

      <input
        type="number"
        placeholder="Sleep Hours"
        className="input"
        value={formData.health.sleep_hours ?? ""}
        onChange={(e) => update("sleep_hours", e.target.value === "" ? "" : Number(e.target.value))}
      />

      <input
        type="number"
        placeholder="Exercise Frequency Per Week"
        className="input"
        value={formData.health.exercise_frequency_per_week ?? ""}
        onChange={(e) =>
          update(
            "exercise_frequency_per_week",
            e.target.value === "" ? "" : Number(e.target.value)
          )
        }
      />

      <select
        className="input"
        value={formData.health.food_pattern ?? ""}
        onChange={(e) => update("food_pattern", e.target.value)}
      >
        <option value="">Food Pattern</option>
        <option value="veg">Veg</option>
        <option value="non_veg">Non Veg</option>
        <option value="mixed">Mixed</option>
      </select>

      <select
        className="input"
        value={formData.health.alcohol ?? ""}
        onChange={(e) => update("alcohol", e.target.value)}
      >
        <option value="">Alcohol Use</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
      </select>

      <select
        className="input"
        value={formData.health.smoking ?? ""}
        onChange={(e) => update("smoking", e.target.value)}
      >
        <option value="">Smoking</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
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
