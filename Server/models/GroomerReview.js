// models/SitterReview.js
import mongoose from "mongoose";

const GroomerReviewSchema = new mongoose.Schema({
 
  groomerappointment: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "GroomerAppointment",
    required: true
  },
  groomer: {
    type: mongoose.Schema.Types.ObjectId,
    ref:"Groomer",
    required: true,
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  },
  text: {
    type: String,
    trim: true,
    maxlength: 1000
  }
}, {
  timestamps: true
});

export default mongoose.model("GroomerReview", GroomerReviewSchema);
