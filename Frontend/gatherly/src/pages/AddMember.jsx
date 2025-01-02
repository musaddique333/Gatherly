import React, {useState} from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import {eventAxiosInstance} from "../axiosInstance";

const AddMember = () => {

    const [eventId, setEventId] = useState("");
    const [userEmail, setUserEmail] = useState("");
    const [organizerEmail, setOrganizerEmail] = useState("");

    const userDetails = {}

    const handleSubmit = (e)=>{
        e.preventDefault();
        eventAxiosInstance.post("/event-members/")
    }

    const handleEventChange = (e) => {
        setEventId(e.target.value);
    }

    const handleUserEmailChange = (e) => {
        setUserEmail(e.target.value);
    }

    const handleOrgEmailChange = (e) => {
        setOrganizerEmail(e.target.value);
    }

    return (
    <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 p-4 max-w-lg mx-auto bg-white shadow-md rounded-lg"
    >
        <h1 className="text-2xl font-bold mb-4">Add Member Form</h1>

        <TextField
        label="Event Id"
        name="Event Id"
        value={eventId}
        onChange={handleEventChange}
        required
        fullWidth
        />

        <TextField
        label="User email"
        name="User email"
        value={userEmail}
        onChange={handleUserEmailChange}
        required
        fullWidth
        />

        <TextField
        label="Organizer email"
        name="Organizer email"
        value={organizerEmail}
        onChange={handleOrgEmailChange}
        required
        fullWidth
        />

        <Button
        type="submit"
        variant="contained"
        color="primary"
        className="mt-4"
        onClick={handleSubmit}
        >
            Add Member
        </Button>

    </form>
    );
};

export default AddMember;