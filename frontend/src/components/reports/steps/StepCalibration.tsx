interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepCalibration({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const update = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      calibration: {
        ...current.calibration,
        [field]: value,
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title mb-2 text-white">Behavior Calibration</h2>

      <select
        className="input"
        value={formData.calibration.stress_response ?? ""}
        onChange={(e) => update("stress_response", e.target.value)}
      >
        <option value="">Stress Response</option>
        <option value="withdraw">Withdraw</option>
        <option value="impulsive">Impulsive</option>
        <option value="overthink">Overthink</option>
        <option value="take_control">Take Control</option>
      </select>

      <select
        className="input"
        value={formData.calibration.money_decision_style ?? ""}
        onChange={(e) => update("money_decision_style", e.target.value)}
      >
        <option value="">Money Decision Style</option>
        <option value="emotional">Emotional</option>
        <option value="calculated">Calculated</option>
        <option value="risky">Risky</option>
        <option value="avoidant">Avoidant</option>
      </select>

      <select
        className="input"
        value={formData.calibration.biggest_weakness ?? ""}
        onChange={(e) => update("biggest_weakness", e.target.value)}
      >
        <option value="">Biggest Weakness</option>
        <option value="discipline">Discipline</option>
        <option value="patience">Patience</option>
        <option value="confidence">Confidence</option>
        <option value="focus">Focus</option>
      </select>

      <select
        className="input"
        value={formData.calibration.life_preference ?? ""}
        onChange={(e) => update("life_preference", e.target.value)}
      >
        <option value="">Life Preference</option>
        <option value="stability">Stability</option>
        <option value="growth">Growth</option>
        <option value="recognition">Recognition</option>
        <option value="freedom">Freedom</option>
      </select>

      <select
        className="input"
        value={formData.calibration.decision_style ?? ""}
        onChange={(e) => update("decision_style", e.target.value)}
      >
        <option value="">Decision Style</option>
        <option value="fast">Fast</option>
        <option value="research">Research</option>
        <option value="advice">Advice</option>
        <option value="emotional">Emotional</option>
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
