'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Download, Trash2, Upload, Plus } from 'lucide-react'
import Image from 'next/image'

interface Document {
  id: string
  name: string
  type: 'personal' | 'payslip'
  uploadDate: string
  size: string
  file?: File // Store the actual file for download
}

export default function DocumentForm() {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: '1',
      name: 'Payslips_20 Aug.pdf',
      type: 'payslip',
      uploadDate: '2024-08-20',
      size: '245 KB',
    },
    {
      id: '2',
      name: 'Payslips_20 Oct.pdf',
      type: 'payslip',
      uploadDate: '2024-10-20',
      size: '312 KB',
    },
  ])

  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    files.forEach((file) => {
      const newDocument: Document = {
        id: Date.now().toString(),
        name: file.name,
        type: 'personal',
        uploadDate: new Date().toISOString().split('T')[0],
        size: `${(file.size / 1024).toFixed(0)} KB`,
        file: file,
      }
      setDocuments((prev) => [...prev, newDocument])
    })
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    files.forEach((file) => {
      const newDocument: Document = {
        id: Date.now().toString(),
        name: file.name,
        type: 'personal',
        uploadDate: new Date().toISOString().split('T')[0],
        size: `${(file.size / 1024).toFixed(0)} KB`,
        file: file,
      }
      setDocuments((prev) => [...prev, newDocument])
    })
  }

  const handleDelete = (id: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id))
  }

  const handleDownload = (doc: Document) => {
    if (doc.file) {
      // Download the actual uploaded file
      const link = document.createElement('a')
      const url = URL.createObjectURL(doc.file)
      link.href = url
      link.download = doc.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } else {
      // For demo files (like the pre-loaded payslips), create a demo file
      const link = document.createElement('a')
      const content = `This is a demo download for: ${doc.name}\nUpload Date: ${doc.uploadDate}\nSize: ${doc.size}`
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)

      link.href = url
      link.download = doc.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }
  }

  const personalDocuments = documents.filter((doc) => doc.type === 'personal')
  const payslips = documents.filter((doc) => doc.type === 'payslip')

  return (
    <div className="space-y-8">
      {/* Personal Documents Section */}
      <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-custom-grey-900">
            Personal Documents
          </h3>
          <Button
            variant="outline"
            size="sm"
            className="h-8 w-8 p-0 rounded-full"
            onClick={() =>
              document.getElementById('personal-file-input-header')?.click()
            }
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <input
          id="personal-file-input-header"
          type="file"
          multiple
          className="hidden"
          onChange={handleFileSelect}
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
        />

        {personalDocuments.length === 0 ? (
          <Card
            className={`border-2 border-dashed transition-colors ${
              isDragOver
                ? 'border-custom-base-green bg-green-50'
                : 'border-custom-grey-300 hover:border-custom-grey-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
              <div className="mb-4">
                <Image
                  src="/images/uploading.png"
                  alt="Upload illustration"
                  width={120}
                  height={120}
                  className="mx-auto"
                />
              </div>
              <h4 className="text-lg font-medium text-custom-grey-900 mb-2">
                Drag & Drop here to upload
              </h4>
              <p className="text-sm text-custom-grey-600 mb-6">
                Or select file from your computer
              </p>
              <Button
                className="bg-custom-grey-900 text-white hover:bg-custom-grey-800"
                onClick={() =>
                  document.getElementById('personal-file-input')?.click()
                }
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload File
              </Button>
              <input
                id="personal-file-input"
                type="file"
                multiple
                className="hidden"
                onChange={handleFileSelect}
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              />
            </div>
          </Card>
        ) : (
          <div className="space-y-3">
            <div className="overflow-hidden border border-custom-grey-200 rounded-lg">
              <table className="w-full">
                <thead className="bg-custom-grey-50">
                  <tr>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Document Name
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Upload Date
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Size
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {personalDocuments.map((document) => (
                    <tr
                      key={document.id}
                      className="border-b border-custom-grey-200 last:border-b-0"
                    >
                      <td className="p-3">
                        <p className="text-sm font-medium text-custom-grey-900">
                          {document.name}
                        </p>
                      </td>
                      <td className="p-3">
                        <p className="text-sm text-custom-grey-600">
                          {new Date(document.uploadDate).toLocaleDateString()}
                        </p>
                      </td>
                      <td className="p-3">
                        <p className="text-sm text-custom-grey-600">
                          {document.size}
                        </p>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => handleDownload(document)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDelete(document.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Payslips Section */}
      <div className="flex flex-col gap-3 space-y-4 mt-6 p-6 border border-custom-grey-200 rounded-3xl">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-custom-grey-900">
            Payslips
          </h3>
          <Button
            variant="outline"
            size="sm"
            className="h-8 w-8 p-0 rounded-full"
            onClick={() =>
              document.getElementById('payslip-file-input-header')?.click()
            }
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <input
          id="payslip-file-input-header"
          type="file"
          multiple
          className="hidden"
          onChange={(e) => {
            const files = Array.from(e.target.files || [])
            files.forEach((file) => {
              const newDocument: Document = {
                id: Date.now().toString(),
                name: file.name,
                type: 'payslip',
                uploadDate: new Date().toISOString().split('T')[0],
                size: `${(file.size / 1024).toFixed(0)} KB`,
                file: file,
              }
              setDocuments((prev) => [...prev, newDocument])
            })
          }}
          accept=".pdf,.doc,.docx"
        />

        {payslips.length === 0 ? (
          <Card className="border border-custom-grey-200">
            <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
              <div className="mb-4">
                <Image
                  src="/images/uploading.png"
                  alt="Upload illustration"
                  width={80}
                  height={80}
                  className="mx-auto opacity-50"
                />
              </div>
              <h4 className="text-lg font-medium text-custom-grey-900 mb-2">
                No payslips uploaded yet
              </h4>
              <p className="text-sm text-custom-grey-600 mb-6">
                Upload payslip documents for this employee
              </p>
              <Button
                className="bg-custom-grey-900 text-white hover:bg-custom-grey-800"
                onClick={() =>
                  document.getElementById('payslip-file-input')?.click()
                }
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload Payslip
              </Button>
              <input
                id="payslip-file-input"
                type="file"
                multiple
                className="hidden"
                onChange={(e) => {
                  const files = Array.from(e.target.files || [])
                  files.forEach((file) => {
                    const newDocument: Document = {
                      id: Date.now().toString(),
                      name: file.name,
                      type: 'payslip',
                      uploadDate: new Date().toISOString().split('T')[0],
                      size: `${(file.size / 1024).toFixed(0)} KB`,
                      file: file,
                    }
                    setDocuments((prev) => [...prev, newDocument])
                  })
                }}
                accept=".pdf,.doc,.docx"
              />
            </div>
          </Card>
        ) : (
          <div className="space-y-3">
            <div className="overflow-hidden border border-custom-grey-200 rounded-lg">
              <table className="w-full">
                <thead className="bg-custom-grey-50">
                  <tr>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Document Name
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Upload Date
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Size
                    </th>
                    <th className="text-left p-3 text-custom-grey-600 text-sm font-medium">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {payslips.map((document) => (
                    <tr
                      key={document.id}
                      className="border-b border-custom-grey-200 last:border-b-0"
                    >
                      <td className="p-3">
                        <p className="text-sm font-medium text-custom-grey-900">
                          {document.name}
                        </p>
                      </td>
                      <td className="p-3">
                        <p className="text-sm text-custom-grey-600">
                          {new Date(document.uploadDate).toLocaleDateString()}
                        </p>
                      </td>
                      <td className="p-3">
                        <p className="text-sm text-custom-grey-600">
                          {document.size}
                        </p>
                      </td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            onClick={() => handleDownload(document)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDelete(document.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
