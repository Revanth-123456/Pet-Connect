// models/SitterReview.js
import mongoose from "mongoose";

const SitterReviewSchema = new mongoose.Schema({
 
  appointment: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "SitterAppointment",
    required: true
  },
  sitter: {
    type: mongoose.Schema.Types.ObjectId,
    ref:"Sitter",
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

export default mongoose.model("SitterReview", SitterReviewSchema);
