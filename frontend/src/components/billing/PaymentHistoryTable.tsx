export default function PaymentHistoryTable({ payments }: any) {
  return (
    <div className="table-shell overflow-x-auto">
      <table className="w-full text-left">
        <thead className="table-head">
          <tr>
            <th className="table-cell">Amount</th>
            <th className="table-cell">Date</th>
            <th className="table-cell">Status</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((payment: any) => (
            <tr key={payment.id} className="table-row">
              <td className="table-cell">INR {payment.amount}</td>
              <td className="table-cell">{payment.created_at}</td>
              <td className="table-cell">{payment.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}