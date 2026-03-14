import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  fetchOrgUsers,
  deleteUser,
  updateUserRole,
  inviteUser,
} from "../../services/adminService";
import AdminUsersTable from "../../components/admin/AdminUsersTable";
import AnimatedButton from "../../components/ui/AnimatedButton";
import DashboardCard from "../../components/ui/DashboardCard";
import PageHero from "../../components/ui/PageHero";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("user");
  const [inviteLoading, setInviteLoading] = useState(false);

  const loadUsers = async () => {
    try {
      const data = await fetchOrgUsers();
      setUsers(data);
    } catch {
      toast.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadUsers();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await deleteUser(id);
      toast.success("User removed");
      await loadUsers();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to delete user");
    }
  };

  const handleRoleChange = async (id: number, role: string) => {
    try {
      await updateUserRole(id, role);
      toast.success("Role updated");
      await loadUsers();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to update role");
    }
  };

  const handleInvite = async () => {
    if (!inviteEmail) {
      toast.error("Email is required");
      return;
    }

    setInviteLoading(true);
    try {
      const res = await inviteUser(inviteEmail, inviteRole);
      toast.success(`User invited. Temporary password: ${res.temporary_password}`);
      setInviteEmail("");
      setInviteRole("user");
      await loadUsers();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to invite user");
    } finally {
      setInviteLoading(false);
    }
  };

  return (
    <div className="premium-page">
      <PageHero
        eyebrow="Workspace / Admin / Users"
        title="Manage organization members with one consistent admin surface."
        description="Invite users, update roles, and review organization members without leaving the design system used across the rest of the dashboard."
        badges={[`${users.length} members`, inviteRole]}
      />

      <DashboardCard title="Invite user" description="Send an invite and assign an initial role.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_180px_180px]">
          <input
            type="email"
            placeholder="Enter email"
            value={inviteEmail}
            onChange={(event) => setInviteEmail(event.target.value)}
            className="input"
          />

          <select
            value={inviteRole}
            onChange={(event) => setInviteRole(event.target.value)}
            className="input"
          >
            <option value="user">User</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>

          <AnimatedButton className="md:col-span-2 xl:col-span-1" onClick={handleInvite} loading={inviteLoading} fullWidth>
            {inviteLoading ? "Inviting..." : "Invite User"}
          </AnimatedButton>
        </div>
      </DashboardCard>

      <DashboardCard
        title="Organization users"
        description={loading ? "Loading organization members." : "Review and manage access across the workspace."}
      >
        <AdminUsersTable users={users} onDelete={handleDelete} onRoleChange={handleRoleChange} />
      </DashboardCard>
    </div>
  );
}