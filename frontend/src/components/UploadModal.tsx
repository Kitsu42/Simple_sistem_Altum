import { Dialog, Transition } from "@headlessui/react";
import { Fragment, useRef, useState } from "react";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

export default function UploadModal({ isOpen, onClose, onUploadSuccess }: UploadModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Selecione um arquivo primeiro.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsUploading(true);
      const res = await fetch("http://localhost:8000/upload-excel/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Erro ao enviar o arquivo.");
      }

      setError("");
      onUploadSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Erro desconhecido.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-gray-800 p-6 text-white shadow-xl transition-all">
                <Dialog.Title className="text-lg font-medium">
                  Importar Arquivo Excel
                </Dialog.Title>

                <input
                  type="file"
                  accept=".xlsx,.xls"
                  ref={fileInputRef}
                  className="mt-4 w-full text-white"
                />

                {error && <p className="text-red-400 mt-2">{error}</p>}

                <div className="mt-6 flex justify-end gap-2">
                  <button
                    className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded"
                    onClick={onClose}
                    disabled={isUploading}
                  >
                    Cancelar
                  </button>
                  <button
                    className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
                    onClick={handleUpload}
                    disabled={isUploading}
                  >
                    {isUploading ? "Enviando..." : "Enviar"}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
