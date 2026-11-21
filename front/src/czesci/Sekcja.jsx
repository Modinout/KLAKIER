export default function Sekcja({ tytul, children }) {
  return (
    <section className="mt-6">
      <h3 className="mb-2 font-medium">{tytul}</h3>
      {children}
    </section>
  )
}
