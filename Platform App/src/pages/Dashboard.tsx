import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getRestaurants, logout, Restaurant } from "../api";

export default function Dashboard() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getRestaurants()
      .then(setRestaurants)
      .finally(() => setLoading(false));
  }, []);

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="layout">
      <header>
        <h1>Platform Admin</h1>
        <button className="btn-outline" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <main>
        <div className="toolbar">
          <h2>Restaurants ({restaurants.length})</h2>
          <Link to="/restaurants/new" className="btn-primary">
            + Add Restaurant
          </Link>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : restaurants.length === 0 ? (
          <p className="empty">No restaurants yet. Add one to get started.</p>
        ) : (
          <div className="card-grid">
            {restaurants.map((r) => (
              <Link
                to={`/restaurants/${r.id}`}
                key={r.id}
                className="card"
                state={r}
              >
                <h3>{r.name}</h3>
                <p>{r.address || "No address"}</p>
                <div className="card-meta">
                  <span className={r.is_active ? "badge active" : "badge"}>
                    {r.is_active ? "Active" : "Inactive"}
                  </span>
                  <span>
                    {r.whatsapp_phone_number_id ? "WhatsApp linked" : "No WhatsApp"}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
