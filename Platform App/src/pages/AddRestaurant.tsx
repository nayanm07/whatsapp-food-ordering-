import { useState, FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createRestaurant } from "../api";

export default function AddRestaurant() {
  const [form, setForm] = useState({ name: "", address: "", phone: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function update(field: string, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await createRestaurant(form);
      navigate("/dashboard");
    } catch {
      setError("Failed to create restaurant");
    }
  }

  return (
    <div className="layout">
      <header>
        <Link to="/dashboard" className="back">&larr; Back</Link>
        <h1>Add Restaurant</h1>
      </header>

      <main>
        <form className="detail-form" onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}
          <label>
            Name *
            <input
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
              required
            />
          </label>
          <label>
            Address
            <input
              value={form.address}
              onChange={(e) => update("address", e.target.value)}
            />
          </label>
          <label>
            Phone
            <input
              value={form.phone}
              onChange={(e) => update("phone", e.target.value)}
            />
          </label>
          <button type="submit" className="btn-primary">Create</button>
        </form>
      </main>
    </div>
  );
}
