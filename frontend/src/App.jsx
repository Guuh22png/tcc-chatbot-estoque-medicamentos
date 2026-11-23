import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000", LIMITE = 30, DIAS = 30;
const PODE = {
  administrador: ["painel", "estoque", "mov", "cad", "usr"],
  tecnico: ["painel", "estoque", "mov"],
};
const PERFIS = { administrador: "Administrador (farmacêutico)", tecnico: "Técnico em enfermagem" };
const TITULOS = { painel: "Painel", estoque: "Estoque", mov: "Movimentações", cad: "Cadastro de medicamentos", usr: "Usuários" };

async function api(path, method = "GET", body) {
  const r = await fetch(API + path, { method, headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof d.detail === "string" ? d.detail : "Não foi possível concluir a operação.");
  return d;
}
const dias = v => (v ? Math.round((new Date(v + "T00:00:00") - new Date().setHours(0, 0, 0, 0)) / 864e5) : null);
const venceLogo = m => { const d = dias(m.validade); return d !== null && d <= DIAS; };

function useForm(ini) {
  const [v, setV] = useState(ini);
  const f = k => ({ value: v[k], onChange: e => setV({ ...v, [k]: e.target.value }) });
  return [v, f, () => setV(ini)];
}

function ValTag({ v }) {
  if (!v) return "—";
  const t = new Date(v + "T00:00:00").toLocaleDateString("pt-BR"), d = dias(v);
  if (d < 0) return <span className="tag low">{t} · vencido</span>;
  if (d <= DIAS) return <span className="tag warn">{t} · {d} dia(s)</span>;
  return t;
}

function Login({ onLogin }) {
  const [v, f] = useForm({ email: "", senha: "" });
  const [erro, setErro] = useState("");
  const enviar = async e => {
    e.preventDefault(); setErro("");
    try { onLogin(await api("/usuarios/login", "POST", v)); } catch (x) { setErro(x.message); }
  };
  return (
    <div id="login" className="card">
      <h3>Entrar no sistema de estoque</h3>
      <form onSubmit={enviar}>
        <label>E-mail<input type="email" required {...f("email")} /></label>
        <label>Senha<input type="password" required {...f("senha")} /></label>
        <button className="go">Entrar</button>
      </form>
      <p className="err">{erro}</p>
    </div>
  );
}

function Painel({ meds, movs, adm }) {
  const nome = Object.fromEntries(meds.map(m => [m.id, m.nome]));
  const baixos = meds.filter(m => m.estoque_atual < LIMITE);
  const venc = meds.filter(venceLogo).sort((a, b) => a.validade.localeCompare(b.validade));
  return (
    <>
      {adm && <div className="kpis">
        <div className="kpi"><span>Medicamentos cadastrados</span><strong>{meds.length}</strong></div>
        <div className="kpi b"><span>Com estoque baixo</span><strong>{baixos.length}</strong></div>
        <div className="kpi w"><span>Vencidos ou vencendo em 30 dias</span><strong>{venc.length}</strong></div>
      </div>}
      <div className="dois">
        <div className="card"><h3>Estoque baixo</h3><ul>
          {baixos.map(m => <li key={m.id}>{m.nome}: <b>{m.estoque_atual} un.</b></li>)}
          {!baixos.length && <li>Nenhum medicamento com estoque baixo.</li>}
        </ul></div>
        <div className="card"><h3>Validade</h3><ul>
          {venc.map(m => <li key={m.id}>{m.nome}: <ValTag v={m.validade} /></li>)}
          {!venc.length && <li>Nenhum vencido ou perto de vencer.</li>}
        </ul></div>
      </div>
      {adm && (
        <div className="card"><h3>Últimas movimentações</h3>
          <table>
            <thead><tr><th>Data</th><th>Medicamento</th><th>Tipo</th><th>Qtd</th><th>Responsável</th></tr></thead>
            <tbody>
              {movs.slice(-5).reverse().map(x => (
                <tr key={x.id}><td>{new Date(x.data + "Z").toLocaleString("pt-BR")}</td><td>{nome[x.medicamento_id] || "removido"}</td>
                  <td>{x.tipo === "entrada" ? "Entrada" : "Saída"}</td><td>{x.quantidade}</td><td>{x.responsavel}</td></tr>
              ))}
              {!movs.length && <tr><td colSpan="5">Nenhuma movimentação.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function Estoque({ meds, adm, acao, onEdit }) {
  const [busca, setBusca] = useState(""), [filtro, setFiltro] = useState("todos");
  const lista = meds.filter(m => m.nome.toLowerCase().includes(busca.toLowerCase()) &&
    (filtro === "todos" || (filtro === "baixo" && m.estoque_atual < LIMITE) || (filtro === "venc" && venceLogo(m))));
  const excluir = id => confirm("Excluir este medicamento?") && acao(() => api("/medicamentos/" + id, "DELETE"));
  return (
    <section className="card">
      <div className="barra">
        <label>Buscar<input placeholder="Nome do medicamento" value={busca} onChange={e => setBusca(e.target.value)} /></label>
        <label>Mostrar<select value={filtro} onChange={e => setFiltro(e.target.value)}>
          <option value="todos">Todos</option><option value="baixo">Estoque baixo</option><option value="venc">Vencidos ou vencendo</option>
        </select></label>
      </div>
      <table>
        <thead><tr><th>ID</th><th>Medicamento</th><th>Atual</th><th>Mínimo</th><th>Validade</th><th>Situação</th>{adm && <th></th>}</tr></thead>
        <tbody>
          {lista.map(m => {
            const baixo = m.estoque_atual < LIMITE;
            return (
              <tr key={m.id}>
                <td>{m.id}</td><td>{m.nome}</td><td>{m.estoque_atual}</td><td>{m.estoque_minimo}</td>
                <td><ValTag v={m.validade} /></td>
                <td><span className={"tag " + (baixo ? "low" : "fine")}>{baixo ? "Estoque baixo" : "OK"}</span></td>
                {adm && <td><button className="go" onClick={() => onEdit(m)}>Editar</button> <button className="del" onClick={() => excluir(m.id)}>Excluir</button></td>}
              </tr>
            );
          })}
          {!lista.length && <tr><td colSpan="7">Nenhum medicamento encontrado.</td></tr>}
        </tbody>
      </table>
    </section>
  );
}

function Mov({ meds, movs, acao, user }) {
  const [v, f, reset] = useForm({ med: "", tipo: "entrada", qtd: "" });
  const [tipo, setTipo] = useState("");
  const nome = Object.fromEntries(meds.map(m => [m.id, m.nome]));
  const enviar = async e => {
    e.preventDefault();
    const body = { medicamento_id: +(v.med || meds[0]?.id), tipo: v.tipo, quantidade: +v.qtd, usuario_id: user.id };
    (await acao(() => api("/movimentacoes/", "POST", body), "Movimentação registrada.")) && reset();
  };
  const lista = movs.filter(x => !tipo || x.tipo === tipo).slice(-30).reverse();
  return (
    <>
      <div className="card">
        <h3>Registrar entrada ou saída</h3>
        <form onSubmit={enviar}>
          <label>Medicamento<select required {...f("med")}>{meds.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}</select></label>
          <label>Tipo<select {...f("tipo")}><option value="entrada">Entrada</option><option value="saida">Saída</option></select></label>
          <label>Quantidade<input type="number" min="1" required {...f("qtd")} /></label>
          <button className="go">Registrar</button>
        </form>
      </div>
      <div className="card">
        <h3>Histórico</h3>
        <div className="barra"><label>Tipo<select value={tipo} onChange={e => setTipo(e.target.value)}>
          <option value="">Todos</option><option value="entrada">Entradas</option><option value="saida">Saídas</option>
        </select></label></div>
        <table>
          <thead><tr><th>Data</th><th>Medicamento</th><th>Tipo</th><th>Qtd</th><th>Responsável</th></tr></thead>
          <tbody>
            {lista.map(x => (
              <tr key={x.id}>
                <td>{new Date(x.data + "Z").toLocaleString("pt-BR")}</td><td>{nome[x.medicamento_id] || "removido"}</td>
                <td>{x.tipo === "entrada" ? "Entrada" : "Saída"}</td><td>{x.quantidade}</td><td>{x.responsavel}</td>
              </tr>
            ))}
            {!lista.length && <tr><td colSpan="5">Nenhuma movimentação.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}

function Cad({ acao, edit, onDone }) {
  const [v, f, reset] = useForm(edit ? { nome: edit.nome, atual: edit.estoque_atual, min: edit.estoque_minimo, val: edit.validade || "" } : { nome: "", atual: "", min: "", val: "" });
  const enviar = async e => {
    e.preventDefault();
    const body = { nome: v.nome, estoque_atual: +v.atual, estoque_minimo: +v.min, validade: v.val || null };
    const ok = edit
      ? await acao(() => api("/medicamentos/" + edit.id, "PUT", body), "Medicamento atualizado.")
      : await acao(() => api("/medicamentos/", "POST", body), "Medicamento cadastrado.");
    if (ok) { reset(); onDone(); }
  };
  return (
    <section className="card">
      <form onSubmit={enviar}>
        <label>Nome<input required {...f("nome")} /></label>
        <label>Estoque atual<input type="number" min="0" required {...f("atual")} /></label>
        <label>Estoque mínimo<input type="number" min="0" required {...f("min")} /></label>
        <label>Validade<input type="date" {...f("val")} /></label>
        <button className="go">{edit ? "Salvar alterações" : "Cadastrar"}</button>{edit && <button type="button" onClick={onDone}>Cancelar</button>}
      </form>
    </section>
  );
}

function Usr({ usrs, acao, eu }) {
  const [v, f, reset] = useForm({ nome: "", email: "", senha: "", perfil: "administrador" });
  const enviar = async e => {
    e.preventDefault();
    (await acao(() => api("/usuarios/", "POST", v), "Usuário criado.")) && reset();
  };
  const alternar = u => acao(() => api(`/usuarios/${u.id}/ativo?ativo=${!u.ativo}`, "PUT"), u.ativo ? "Usuário desativado." : "Usuário reativado.");
  return (
    <>
      <div className="card">
        <h3>Criar usuário</h3>
        <form onSubmit={enviar}>
          <label>Nome<input required {...f("nome")} /></label>
          <label>E-mail<input type="email" required {...f("email")} /></label>
          <label>Senha<input type="password" required {...f("senha")} /></label>
          <label>Perfil<select {...f("perfil")}>
            <option value="administrador">Administrador (farmacêutico)</option><option value="tecnico">Técnico em enfermagem</option>
          </select></label>
          <button className="go">Criar usuário</button>
        </form>
      </div>
      <div className="card">
        <h3>Usuários cadastrados</h3>
        <table>
          <thead><tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Perfil</th><th>Status</th><th></th></tr></thead>
          <tbody>{usrs.map(u => (
            <tr key={u.id}><td>{u.id}</td><td>{u.nome}</td><td>{u.email}</td><td>{PERFIS[u.perfil] || u.perfil}</td><td>{u.ativo ? "Ativo" : "Inativo"}</td>
              <td>{u.id !== eu && <button className={u.ativo ? "del" : "go"} onClick={() => alternar(u)}>{u.ativo ? "Desativar" : "Reativar"}</button>}</td></tr>
          ))}</tbody>
        </table>
      </div>
    </>
  );
}

export default function App() {
  const [user, setUser] = useState(() => { try { return JSON.parse(sessionStorage.getItem("u")); } catch { return null; } });
  const [aba, setAba] = useState("painel");
  const [meds, setMeds] = useState([]), [movs, setMovs] = useState([]), [usrs, setUsrs] = useState([]);
  const [msg, setMsg] = useState({ t: "", ok: false });
  const [editando, setEditando] = useState(null);

  const aviso = (t, ok = false) => { setMsg({ t, ok }); setTimeout(() => setMsg({ t: "", ok: false }), 4000); };
  const carregar = async () => {
    if (!user) return;
    try {
      setMeds(await api("/medicamentos/"));
      if (PODE[user.perfil].includes("mov")) setMovs(await api("/movimentacoes/"));
      if (user.perfil === "administrador") setUsrs(await api("/usuarios/"));
    } catch (e) { aviso(e.message); }
  };
  useEffect(() => { carregar(); }, [user]);

  const acao = async (fn, ok) => {
    try { await fn(); if (ok) aviso(ok, true); carregar(); return true; }
    catch (e) { aviso(e.message); return false; }
  };
  const entrar = u => { try { sessionStorage.setItem("u", JSON.stringify(u)); } catch {} setAba("painel"); setUser(u); };
  const sair = () => { try { sessionStorage.removeItem("u"); } catch {} setUser(null); };

  if (!user) return <Login onLogin={entrar} />;
  const menu = PODE[user.perfil] || ["painel", "estoque"];

  return (
    <div className="layout">
      <aside className="side">
        <h1>Estoque de Medicamentos</h1>
        {menu.map(k => <button key={k} className={aba === k ? "on" : ""} onClick={() => { setEditando(null); setAba(k); }}>{TITULOS[k]}</button>)}
        <div className="user"><span>{user.nome} ({PERFIS[user.perfil] || user.perfil})</span><button onClick={sair}>Sair</button></div>
      </aside>
      <main className="content">
        <h2 className="titulo">{TITULOS[aba]}</h2>
        <p id="msg" role="status" style={{ color: msg.ok ? "var(--ok)" : "var(--bad)" }}>{msg.t}</p>
        {aba === "painel" && <Painel meds={meds} movs={movs} adm={user.perfil === "administrador"} />}
        {aba === "estoque" && <Estoque meds={meds} adm={user.perfil === "administrador"} acao={acao} onEdit={m => { setEditando(m); setAba("cad"); }} />}
        {aba === "mov" && <Mov meds={meds} movs={movs} acao={acao} user={user} />}
        {aba === "cad" && <Cad key={editando?.id || "novo"} acao={acao} edit={editando} onDone={() => setEditando(null)} />}
        {aba === "usr" && <Usr usrs={usrs} acao={acao} eu={user.id} />}
      </main>
    </div>
  );
}
