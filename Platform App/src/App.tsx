import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import RestaurantDetail from "./pages/RestaurantDetail";
import AddRestaurant from "./pages/AddRestaurant";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("token");
  return token ? <>{children}</> : <Navigate to="/" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/restaurants/new"
          element={
            <PrivateRoute>
              <AddRestaurant />
            </PrivateRoute>
          }
        />
        <Route
          path="/restaurants/:id"
          element={
            <PrivateRoute>
              <RestaurantDetail />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
