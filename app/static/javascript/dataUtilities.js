
async function retrieveData(table, dbId, cols) {
    try {
        const response = await fetch(`/get-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': window.CSRF_TOKEN,
            },
            body: JSON.stringify({
                table: table,
                id: dbId,
                columns: cols,
            })
        });
        if (!response.ok) {
            console.error("Failure to retrieve data")
            return null;
        } else {
            const data = await response.json();
            return data;
        }

    } catch (error) {
        console.error(error);
        return null;
    }


}

async function deleteData(table, dbId) {
    try {
        const response = await fetch("/delete", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': window.CSRF_TOKEN,
            },
            body: JSON.stringify({
                table: table,
                id: dbId,
            })
        });
        if (!response.ok) {
            throw new Error(`Delete failed: ${response.status} ${response.statusText}`)
        } else {
            return true;
        }
    } catch (error) {
        console.error(error);
        throw error;
    }
}

async function populateData(table, dbId, cols) {
    const data = await retrieveData(table, dbId, cols);
    if (data) {
        cols.forEach(col => {
            const element = document.getElementById(col);
            if (element) {

                if (CKEDITOR.instances[col]) {
                    CKEDITOR.instances[col].setData(data[col]);
                }else {
                    element.value = data[col];
                }
                

            } else {
                console.warn(`Element with ID "${col}" not found`)
            }

        })

    } else {
        console.warn('Populate data failure')
    }

}