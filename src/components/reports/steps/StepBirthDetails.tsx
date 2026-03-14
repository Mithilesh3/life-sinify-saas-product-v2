interface Props {
  formData: any;
  setFormData: (value: any) => void;
  next: () => void;
  prev: () => void;
}

export default function StepBirthDetails({
  formData,
  setFormData,
  next,
  prev,
}: Props) {
  const update = (field: string, value: string) => {
    setFormData((current: any) => ({
      ...current,
      birth_details: {
        ...current.birth_details,
        [field]: value,
      },
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="surface-title text-white">Birth Details</h2>

      <input
        type="date"
        className="input"
        value={formData.birth_details.date_of_birth ?? ""}
        onChange={(e) => update("date_of_birth", e.target.value)}
      />

      <input
        placeholder="Time of Birth"
        className="input"
        value={formData.birth_details.time_of_birth ?? ""}
        onChange={(e) => update("time_of_birth", e.target.value)}
      />

      <input
        placeholder="Birth City"
        className="input"
        value={formData.birth_details.birthplace_city ?? ""}
        onChange={(e) => update("birthplace_city", e.target.value)}
      />

      <input
        placeholder="Birth Country"
        className="input"
        value={formData.birth_details.birthplace_country ?? ""}
        onChange={(e) => update("birthplace_country", e.target.value)}
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
