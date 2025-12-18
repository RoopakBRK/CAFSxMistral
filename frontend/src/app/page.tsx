import React from "react"
import UploadForm from "@/components/verification/UploadForm"
import Navbar from "@/components/ui/Navbar"
import { HeroGrid } from "@/components/ui/HeroGrid"
import { HowItWorks } from "@/components/ui/HowItWorks"
import { LogoCarousel, Logo } from "@/components/ui/LogoCarousel"

const logos: Logo[] = [
  { id: 1, name: "Udemy", src: "/logos/udemy.svg" },
  { id: 2, name: "Coursera", src: "/logos/coursera.svg" },
  { id: 3, name: "edX", src: "/logos/edx.svg" },
  { id: 4, name: "W3Schools", src: "/logos/w3schools.svg" },
  { id: 5, name: "IBM", src: "/logos/ibm.svg" },
  { id: 6, name: "Cisco", src: "/logos/cisco.svg" },
  { id: 7, name: "Google", src: "/logos/google.svg" },
  { id: 8, name: "LinkedIn", src: "/logos/linkedin.svg" },
  { id: 9, name: "Oracle", src: "/logos/oracle.svg" },
]

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      {/* Navbar */}
      <Navbar />

      {/* Hero Section */}
      <HeroGrid />

      {/* Trusted Issuers Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-6">

          {/* Grey container */}
          <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-3xl py-16 px-8 md:px-20 shadow-sm border border-slate-200/50">

            <div className="text-center mb-12">
              <h3 className="text-3xl md:text-4xl font-bold text-slate-900 mb-3">
                Trusted by Leading Platforms
              </h3>
              <p className="text-slate-600 text-base md:text-lg max-w-2xl mx-auto">
                Instant verification from world-class certificate issuers
              </p>
            </div>

            {/* Logos - Centered */}
            <div className="flex justify-center items-center">
              <div className="w-full max-w-6xl">
                <LogoCarousel logos={logos} columnCount={3} />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section
        id="verify"
        className="bg-white flex flex-col items-center justify-center px-4 py-20"
      >
        <div className="text-center mb-12 max-w-3xl">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Start Verification
          </h2>
          <p className="text-lg text-slate-600">
            Upload your certificate and get instant verification results
          </p>
        </div>

        <div className="w-full max-w-md">
          <UploadForm />
        </div>
      </section>

      {/* How It Works */}
      <HowItWorks />
    </main>
  )
}