import { useState } from "react";

export default function useModal() {
    const [isOpen, set_isOpen] = useState(false);

    const toggle = () => {
        set_isOpen(!isOpen);
    };

    return {
        isOpen,
        toggle
    };
}