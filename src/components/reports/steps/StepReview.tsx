interface Props {
  prev: () => void;
  submit: () => void;
  submitting?: boolean;
  plan?: string;
}

export default function StepReview({
  prev,
  submit,
  submitting,
  plan,
}: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="surface-title mb-2 text-white">Review and Generate</h2>
        <p className="type-body text-slate-400">
          The final payload will be sent using the backend's current intake schema for the {plan?.toUpperCase() ?? "CURRENT"} plan.
        </p>
      </div>

      <div className="flex justify-between">
        <button onClick={prev} className="btn-secondary">
          Back
        </button>

        <button
          onClick={submit}
          disabled={submitting}
          className="btn-primary disabled:opacity-50"
        >
          {submitting ? "Generating..." : "Generate Report"}
        </button>
      </div>
    </div>
  );
}
