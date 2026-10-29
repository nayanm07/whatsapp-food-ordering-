import { useState, useEffect, FormEvent } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import { getRestaurants, updateRestaurant, setWhatsAppConfig, Restaurant } from "../api";

export default function RestaurantDetail() {
  const { state } = useLocation() as { state: Restaurant | null };
  const { id } = useParams<{ id: string }>();

  const [restaurant, setRestaurant] = useState<Restaurant | null>(state);
  const [loading, setLoading] = useState(!state);
  const [tab, setTab] = useState<"details" | "whatsapp">("details");

  const [form, setForm] = useState({
    name: state?.name || "",
    address: state?.address || "",
    phone: state?.phone || "",
    opening_time: state?.opening_time || "09:00",
    closing_time: state?.closing_time || "22:00",
    free_delivery_distance_km: state?.free_delivery_distance_km ?? 3,
    delivery_charge_per_km: state?.delivery_charge_per_km ?? 10,
    is_active: state?.is_active ?? true,
  });

  const [wa, setWa] = useState({
    whatsapp_phone_number_id: state?.whatsapp_phone_number_id || "",
    whatsapp_access_token: "",
  });

  const [msg, setMsg] = useState("");
  const [msgType, setMsgType] = useState<"success" | "error">("success");
  const [copiedField, setCopiedField] = useState("");

  const webhookUrl = `${window.location.origin}/api/webhook/whatsapp`;
  const verifyToken = "foodorder_webhook_2024";

  function copyToClipboard(text: string, field: string) {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(""), 2000);
  }

  useEffect(() => {
    if (state) return;
    getRestaurants().then((list) => {
      const found = list.find((r) => r.id === Number(id));
      if (found) {
        setRestaurant(found);
        setForm({
          name: found.name,
          address: found.address || "",
          phone: found.phone || "",
          opening_time: found.opening_time,
          closing_time: found.closing_time,
          free_delivery_distance_km: found.free_delivery_distance_km,
          delivery_charge_per_km: found.delivery_charge_per_km,
          is_active: found.is_active,
        });
        setWa((w) => ({
          ...w,
          whatsapp_phone_number_id: found.whatsapp_phone_number_id || "",
        }));
      }
      setLoading(false);
    });
  }, [id, state]);

  function showMsg(text: string, type: "success" | "error" = "success") {
    setMsg(text);
    setMsgType(type);
    setTimeout(() => setMsg(""), 3000);
  }

  function update(field: string, value: string | number | boolean) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    try {
      const updated = await updateRestaurant(id!, form);
      setRestaurant(updated);
      showMsg("Restaurant updated!");
    } catch {
      showMsg("Failed to update", "error");
    }
  }

  async function handleWhatsApp(e: FormEvent) {
    e.preventDefault();
    if (!wa.whatsapp_phone_number_id || !wa.whatsapp_access_token) {
      showMsg("Both fields are required", "error");
      return;
    }
    try {
      const updated = await setWhatsAppConfig(id!, wa);
      setRestaurant(updated);
      setWa((w) => ({ ...w, whatsapp_access_token: "" }));
      showMsg("WhatsApp connected successfully!");
    } catch {
      showMsg("Failed to save WhatsApp config", "error");
    }
  }

  if (loading) return <div className="layout"><p>Loading...</p></div>;
  if (!restaurant) return <div className="layout"><p>Restaurant not found.</p></div>;

  const waConnected = !!restaurant.whatsapp_phone_number_id;

  return (
    <div className="layout">
      <header>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <Link to="/dashboard" className="back">&larr; Back</Link>
          <h1>{restaurant.name}</h1>
        </div>
        <div className={waConnected ? "wa-status connected" : "wa-status"}>
          <span className="wa-dot" />
          {waConnected ? "WhatsApp Connected" : "WhatsApp Not Connected"}
        </div>
      </header>

      {msg && <div className={msgType === "success" ? "success" : "error"}>{msg}</div>}

      <div className="tabs">
        <button
          className={tab === "details" ? "tab active" : "tab"}
          onClick={() => setTab("details")}
        >
          Restaurant Details
        </button>
        <button
          className={tab === "whatsapp" ? "tab active" : "tab"}
          onClick={() => setTab("whatsapp")}
        >
          WhatsApp Config
          {!waConnected && <span className="tab-badge">Setup Required</span>}
        </button>
      </div>

      <main>
        {tab === "details" && (
          <form className="detail-form" onSubmit={handleSave}>
            <div className="form-row">
              <label>
                Name
                <input value={form.name} onChange={(e) => update("name", e.target.value)} />
              </label>
              <label>
                Phone
                <input value={form.phone} onChange={(e) => update("phone", e.target.value)} />
              </label>
            </div>
            <label>
              Address
              <input value={form.address} onChange={(e) => update("address", e.target.value)} />
            </label>
            <div className="form-row">
              <label>
                Opening Time
                <input type="time" value={form.opening_time} onChange={(e) => update("opening_time", e.target.value)} />
              </label>
              <label>
                Closing Time
                <input type="time" value={form.closing_time} onChange={(e) => update("closing_time", e.target.value)} />
              </label>
            </div>
            <div className="form-row">
              <label>
                Free Delivery Distance (km)
                <input type="number" step="0.5" value={form.free_delivery_distance_km} onChange={(e) => update("free_delivery_distance_km", +e.target.value)} />
              </label>
              <label>
                Delivery Charge / km
                <input type="number" step="1" value={form.delivery_charge_per_km} onChange={(e) => update("delivery_charge_per_km", +e.target.value)} />
              </label>
            </div>
            <label className="checkbox-label">
              <input type="checkbox" checked={form.is_active} onChange={(e) => update("is_active", e.target.checked)} />
              Active
            </label>
            <button type="submit" className="btn-primary">Save Changes</button>
          </form>
        )}

        {tab === "whatsapp" && (
          <div>
            <div className={waConnected ? "wa-card connected" : "wa-card"}>
              <div className="wa-card-icon">{waConnected ? "✓" : "!"}</div>
              <div>
                <strong>{waConnected ? "WhatsApp Business Connected" : "WhatsApp Not Configured"}</strong>
                <p>
                  {waConnected
                    ? `Phone Number ID: ${restaurant.whatsapp_phone_number_id}`
                    : "Connect a WhatsApp Business number so customers can order from this restaurant."}
                </p>
              </div>
            </div>

            <div className="webhook-box">
              <div className="webhook-label">Webhook URL (same for all restaurants)</div>
              <div className="webhook-row">
                <code className="webhook-url">{webhookUrl}</code>
                <button type="button" className="btn-copy" onClick={() => copyToClipboard(webhookUrl, "url")}>
                  {copiedField === "url" ? "Copied!" : "Copy"}
                </button>
              </div>
              <span className="hint">Paste in Meta App Dashboard &rarr; WhatsApp &rarr; Configuration &rarr; Callback URL</span>

              <div className="webhook-label" style={{ marginTop: "1rem" }}>Verify Token</div>
              <div className="webhook-row">
                <code className="webhook-url">{verifyToken}</code>
                <button type="button" className="btn-copy" onClick={() => copyToClipboard(verifyToken, "token")}>
                  {copiedField === "token" ? "Copied!" : "Copy"}
                </button>
              </div>
              <span className="hint">Paste in Meta App Dashboard &rarr; WhatsApp &rarr; Configuration &rarr; Verify Token</span>

              <p className="webhook-note">
                All restaurants share one webhook. When a customer sends a message, Meta includes the Phone Number ID in the payload — the system uses it to identify which restaurant the message belongs to.
              </p>
            </div>

            <form className="detail-form" onSubmit={handleWhatsApp}>
              <h3 style={{ marginBottom: "1rem", fontSize: "0.95rem" }}>
                {waConnected ? "Update WhatsApp Credentials" : "Connect WhatsApp Business"}
              </h3>
              <label>
                Phone Number ID
                <input
                  value={wa.whatsapp_phone_number_id}
                  onChange={(e) => setWa((w) => ({ ...w, whatsapp_phone_number_id: e.target.value }))}
                  placeholder="e.g. 100234567890123"
                />
                <span className="hint">Found in Meta Business Manager &rarr; WhatsApp &rarr; API Setup</span>
              </label>
              <label>
                Access Token
                <input
                  type="password"
                  value={wa.whatsapp_access_token}
                  onChange={(e) => setWa((w) => ({ ...w, whatsapp_access_token: e.target.value }))}
                  placeholder="Permanent access token from Meta"
                />
                <span className="hint">Generate a permanent token in Meta Business Settings &rarr; System Users</span>
              </label>
              <button type="submit" className="btn-primary">
                {waConnected ? "Update Config" : "Connect WhatsApp"}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
