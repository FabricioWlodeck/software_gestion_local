import { useState, type FormEvent } from "react";
import { ErrorApi } from "../../api/cliente";
import { useSesion } from "./sesion";
import "./auth.css";

// Formulario de inicio de sesión. Si sale bien, el contexto cambia y App muestra la caja.
export function PantallaLogin() {
  const { iniciarSesion } = useSesion();
  const [nombre, setNombre] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault(); // evita que el navegador recargue la página al enviar el formulario
    setEnviando(true);
    setError(null);
    try {
      await iniciarSesion(nombre, contrasena);
    } catch (problema) {
      setError(problema instanceof ErrorApi ? problema.message : "No se pudo conectar con el servidor");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="login" onSubmit={enviar}>
      <h2>Iniciar sesión</h2>
      <label>
        Usuario
        <input value={nombre} onChange={(evento) => setNombre(evento.target.value)} autoComplete="username" required />
      </label>
      <label>
        Contraseña
        <input
          type="password"
          value={contrasena}
          onChange={(evento) => setContrasena(evento.target.value)}
          autoComplete="current-password"
          required
        />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={enviando}>
        {enviando ? "Ingresando…" : "Ingresar"}
      </button>
    </form>
  );
}
