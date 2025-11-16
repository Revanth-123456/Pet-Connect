// controllers/reviews.js
import jwt         from "jsonwebtoken";
import GroomerReview  from "../models/GroomerReview.js";
import {Appointment  as GroomerAppointment} from "../models/GroomerAppointment.js";



export const CreateGroomerReview = async (req, res) => {
  // 1) Auth: pet-owner token
  const token = req.cookies.pet_ownerToken;
  if (!token) {
    return res.status(401).json({ message: "Unauthorized – please log in" });
  }

  let decoded;
  try {
    decoded = jwt.verify(token, process.env.JWT_SECRET);
  } catch (err) {
    return res.status(401).json({ message: "Unauthorized – invalid token" });
  }
  const userId = decoded.id;

  // 2) Body params
  const {groomerappointmentId,  groomerId , rating, review: text } = req.body;
  if (!groomerappointmentId || !groomerId || !rating) {
    return res.status(400).json({ message: "Missing required fields" });
  }
  if (rating < 1 || rating > 5) {
    return res.status(400).json({ message: "Rating must be between 1 and 5" });
  }

  try {
    // 3) Check appointment
    const appt = await GroomerAppointment.findById(groomerappointmentId);
    if (!appt) {
      return res.status(404).json({ message: "Appointment not found" });
    }
    if (appt.userId.toString() !== userId) {
      return res.status(403).json({ message: "You did not book this appointment" });
    }
    if (appt.sitterId.toString() !== groomerId) {
      return res.status(400).json({ message: "Invalid provider for this appointment" });
    }
    if (appt.status !== "completed") {
      return res.status(400).json({ message: "You can only review completed appointments" });
    }

    // 4) Prevent duplicate
    const existing = await SitterReview.findOne({ groomerappointment: groomerappointmentId });
    if (existing) {
      return res.status(409).json({ message: "You have already reviewed this appointment" });
    }

    // 5) Create & save
    const newGroomerReview = new GroomerReview({
      groomerappointment: groomerappointmentId,
      groomer:    groomerId,
      user:        userId,
      rating,
      text
    });
    await newGroomerReview.save();

    res.status(201).json({ message: "Review submitted successfully" });
  } catch (err) {
    console.error("Error in CreateReview:", err);
    res.status(500).json({ message: "Internal server error" });
  }
};




