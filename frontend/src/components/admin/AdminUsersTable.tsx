interface Props {
  users: any[];
  onDelete: (id: number) => void;
  onRoleChange: (id: number, role: string) => void;
}

export default function AdminUsersTable({ users, onDelete, onRoleChange }: Props) {
  if (!users.length) {
    return <p className="type-body">No users found in this organization.</p>;
  }

  return (
    <div className="table-shell overflow-x-auto">
      <table className="min-w-[640px] w-full text-left">
        <thead className="table-head">
          <tr>
            <th className="table-cell">Email</th>
            <th className="table-cell">Role</th>
            <th className="table-cell">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="table-row">
              <td className="table-cell">{user.email}</td>
              <td className="table-cell">
                <select
                  value={user.role}
                  onChange={(event) => onRoleChange(user.id, event.target.value)}
                  className="input max-w-[160px] !py-2"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="user">User</option>
                </select>
              </td>
              <td className="table-cell">
                <button onClick={() => onDelete(user.id)} className="btn-secondary !px-3 !py-2 text-[14px]">
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}