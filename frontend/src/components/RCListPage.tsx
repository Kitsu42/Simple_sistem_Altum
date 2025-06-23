import { useEffect, useState } from "react";
import { Upload } from "lucide-react";
import dayjs from "dayjs";
import Modal from "./UploadModal"; // modal separado

interface RC {
  id: number;
  requester_name: string;
  description: string;
  status: string;
  created_at: string;
}

export default function RCListPage() {
  const [rcs, setRcs] = useState<RC[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchRCs();
  }, []);

  const fetchRCs = () => {
    setLoading(true);
    fetch("http://localhost:8000/purchase-request/")
      .then((res) => res.json())
      .then((data) => {
        setRcs(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const getCardColor = (createdAt: string) => {
    const dias = dayjs().diff(dayjs(createdAt), "day");
    if (dias > 10) return "bg-red-600";
    if (dias > 5) return "bg-yellow-600";
    return "bg-gray-800";
  };

  return (
    <div className="min-h-screen w-full bg-gray-900 text-white flex flex-col">
      <div className="bg-gray-800 p-4 flex items-center justify-between shadow-md">
        <h1 className="text-2xl font-bold">Requisições de Compra</h1>
        <div className="flex gap-2">
          <button className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm">
            Concluídas
          </button>
          <button className="bg-yellow-500 hover:bg-yellow-600 px-3 py-1 rounded text-sm">
            Em Cotação
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 p-2 rounded"
            title="Importar Planilha"
          >
            <Upload size={16} />
          </button>
        </div>
      </div>

      <div className="p-4 overflow-y-auto max-h-[calc(100vh-80px)] grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <p>Carregando RCs...</p>
        ) : rcs.length === 0 ? (
          <p>Nenhuma RC encontrada.</p>
        ) : (
          rcs.map((rc) => {
            const dias = dayjs().diff(dayjs(rc.created_at), "day");
            return (
              <div
                key={rc.id}
                className={`${getCardColor(rc.created_at)} p-4 rounded shadow transition-all`}
              >
                <p><strong>ID:</strong> {rc.id}</p>
                <p><strong>Solicitante:</strong> {rc.requester_name}</p>
                <p><strong>Status:</strong> {rc.status}</p>
                <p><strong>Dias em aberto:</strong> {dias} dias</p>
              </div>
            );
          })
        )}
      </div>

      {showModal && (
        <Modal
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setShowModal(false);
            fetchRCs();
          }}
        />
      )}
    </div>
  );
}