import React, {useState} from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import {eventAxiosInstance} from "../axiosInstance";
import { useLocation, useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';


const AddReminder = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
    event_id: "",
    reminder_time: "",
    user_email: localStorage.getItem("userId"),
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
          ...formData,
          [name]: value,
        });
      };

    const handleSubmit = (e)=>{
        e.preventDefault();
        const formattedDate = new Date(formData.reminder_time).toISOString();

        const reminderData = {
            ...formData,
            date: formattedDate,
        };

        eventAxiosInstance
        .post("/reminder/", reminderData)
        .then((response) => {
            // Show success message with SweetAlert
            Swal.fire({
            icon: "success",
            title: "Reminder Created Successfully",
            text: "Your reminder has been successfully created and added.",
            })
            .then(() => {
                navigate("/user/reminders");
            });
        })
        .catch((error) => {
        // Show error message with SweetAlert
        Swal.fire({
            icon: "error",
            title: "reminder Creation Failed",
            text: error.response?.data?.message || "Something went wrong.",
        });
        });
    };


    return (
    <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 p-4 max-w-lg mx-auto bg-white shadow-md rounded-lg"
    >
        <h1 className="text-2xl font-bold mb-4">Add Reminder</h1>

        <TextField
        label="Event Id"
        name="event_id"
        value={formData.event_id}
        onChange={handleChange}
        required
        fullWidth
        />

        <TextField
        label="Reminder Time"
        name="reminder_time"
        type="datetime-local"
        value={formData.reminder_time}
        onChange={handleChange}
        required
        InputLabelProps={{ shrink: true }}
        fullWidth
        />

        <Button
        type="submit"
        variant="contained"
        color="primary"
        className="mt-4"
        >
            Add Reminder
        </Button>

    </form>
    );
};

export default AddReminder;
