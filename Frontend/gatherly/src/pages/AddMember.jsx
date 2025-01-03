import React, {useState} from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import {eventAxiosInstance} from "../axiosInstance";
import { useLocation } from "react-router-dom";

const AddMember = () => {
    const [userEmail, setUserEmail] = useState("");
    const location = useLocation();
    const eventId = location.state?.eventdata.id;

    const handleSubmit = (e)=>{
        e.preventDefault();
        eventAxiosInstance.post("/event-members/", {
            params:{
                member:{
                    event_id:eventId,
                    user_email: userEmail,
                },
                organizer_email: userId
            }
        })
    }

    const handleUserEmailChange = (e) => {
        setUserEmail(e.target.value);
    }

    return (
    <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 p-4 max-w-lg mx-auto bg-white shadow-md rounded-lg"
    >
        <h1 className="text-2xl font-bold mb-4">Add Member Form</h1>

        <TextField
        label="User email"
        name="User email"
        value={userEmail}
        onChange={handleUserEmailChange}
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