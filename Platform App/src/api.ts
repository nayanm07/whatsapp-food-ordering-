const BASE = "/api/admin";

export interface Restaurant {
  id: number;
  name: string;
  address: string | null;
  phone: string | null;
  logo_url: string | null;
  whatsapp_phone_number_id: string | null;
  free_delivery_distance_km: number;
  delivery_charge_per_km: number;
  opening_time: string;
  closing_time: string;
  is_active: boolean;
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const token = localStorage.getItem("token");
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  return data;
}

export async function getRestaurants(): Promise<Restaurant[]> {
  const res = await fetch(`${BASE}/restaurants`, { headers: headers() });
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/";
    return [];
  }
  return res.json();
}

export async function createRestaurant(data: Partial<Restaurant>) {
  const res = await fetch(`${BASE}/restaurants`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create restaurant");
  return res.json();
}

export async function updateRestaurant(id: number | string, data: Partial<Restaurant>) {
  const res = await fetch(`${BASE}/restaurants/${id}`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update restaurant");
  return res.json();
}

export async function setWhatsAppConfig(
  id: number | string,
  data: { whatsapp_phone_number_id: string; whatsapp_access_token: string }
) {
  const res = await fetch(`${BASE}/restaurants/${id}/whatsapp`, {
    method: "PUT",
    headers: headers(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update WhatsApp config");
  return res.json();
}

export function logout() {
  localStorage.removeItem("token");
}
