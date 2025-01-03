import React, {useState} from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import {eventAxiosInstance} from "../axiosInstance";
import { useLocation } from "react-router-dom";

const AddReminder = () => {
    const [eventId, setEventId] = useState("");
    const [reminderTime, setReminderTime] = useState("");

    const handleSubmit = (e)=>{
        e.preventDefault();
        const formattedDate = new Date(reminderTime).toISOString();
        console.log("event" + eventId);
        console.log("reminder" + reminderTime);
        console.log("Formatted" + formattedDate);
        console.log(localStorage.getItem("userId"));
        eventAxiosInstance.post("/reminder/", {
            params:{
                event_id:eventId,
                user_email: localStorage.getItem("userId"),
                reminder_time: formattedDate
            }
        })
    }

    const handleEventIdChange = (e) => {
        setEventId(e.target.value);
    }

    const handleReminderTimeChange = (e) => {
        setReminderTime(e.target.value);
    }

    return (
    <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 p-4 max-w-lg mx-auto bg-white shadow-md rounded-lg"
    >
        <h1 className="text-2xl font-bold mb-4">Add Reminder</h1>

        <TextField
        label="Event Id"
        name="Event Id"
        value={eventId}
        onChange={handleEventIdChange}
        required
        fullWidth
        />

        <TextField
        label="Reminder Time"
        name="Reminder Time"
        type="datetime-local"
        value={reminderTime}
        onChange={handleReminderTimeChange}
        required
        InputLabelProps={{ shrink: true }}
        fullWidth
        />

        <Button
        type="submit"
        variant="contained"
        color="primary"
        className="mt-4"
        onClick={handleSubmit}
        >
            Add Reminder
        </Button>

    </form>
    );
};

export default AddReminder;