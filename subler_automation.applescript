//Get list of files in a folder
function listFilePaths(folderPath, extension) {
    const folder = Application('System Events').folders.byName(folderPath);
    const files = folder.files.name();
    const subfolders = folder.folders.name();
    let allFiles = files.filter(file => file.endsWith(extension)).map(file => `${folderPath}/${file}`);
    subfolders.forEach(subfolder => {
        const subfolderPath = `${folderPath}/${subfolder}`;
        allFiles = allFiles.concat(listFilePaths(subfolderPath, extension));
    });
    return allFiles.sort();
}

// Main Execution
function run() {

    // Define the folder paths
    const mkvFolderilePath = "~/workspace/multiple-dvdrip/output/mkv";
	const mp4FolderilePath = "~/workspace/multiple-dvdrip/output/mp4";

    // Print the list of files in the folder
    const mkvFiles = listFilePaths(mkvFolderilePath, ".mkv");
    const mp4Files = listFilePaths(mp4FolderilePath, ".mp4");

    mkvFiles.forEach(file => console.log(file));
    console.log("the end");
}