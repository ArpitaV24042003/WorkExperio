import { Link } from "react-router-dom";
import bg from "../assets/pixelOffice.png";



export default function LandingPage() {
  return (
    <div
      className="min-h-screen bg-cover bg-center flex flex-col items-center justify-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <h1 className="text-5xl font-bold text-white mb-4 drop-shadow-[0_3px_5px_rgba(0,0,0,0.7)]">
        WorkExperio
      </h1>
      <p className="text-lg text-white max-w-xl text-center mb-8 drop-shadow-[0_3px_5px_rgba(0,0,0,0.7)]">
        Revolutionizing Project Management with AI-Driven Team Formation & Performance Analysis

      </p>
      <Link to="/login">
        <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium px-8 py-3 rounded-lg transition">
          Get Started
        </button>
      </Link>
    </div>
  );
}
