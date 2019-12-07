window.addEventListener('load', function() 
{
	generateRows(60);
});

//Generates the rows of results. Takes a length which is the number of amino acids per row
function generateRows(length)
{
	//Get pdbdata and majority if they exist
	var pdbdata = null;
	var majority = null;
	
	var seq = '';
	var sites = []; //array containing data of sites that are completed

	for (i = 0; i < a.length; i++)
	{
		if ('majority' in a[i]) 
		{ 
			majority = a[i]['majority'];
		}
		
		if ('pdbid' in a[i]) 
		{ 
			pdbdata = a[i];
		}
		
		if ('sequence' in a[i]) 
		{ 
			seq = a[i]['sequence'];
		}
		
		if('status' in a[i] && a[i]['status'] == 1 || a[i]['status'] == 3)
		{
			sites.push(a[i]);
		}
	}
	
	var rows = 0;
	rows = Math.ceil(seq.length/length)
	
	var counter = drawCounter(seq);
	var output = "";
	for(var i = 0; i < rows; i++)
	{
		//counter row
		output += "<tr class='counterRow'><td align='right'></td>";
		output += "<td class='charCounter'>" + counter.substring(length * i, length * (i + 1)).replace(/ /g, "&nbsp;") + "</td></tr>"; //replace afterwards so that &nbsp will not be substringed out
		
		//sequence row
		output += "<tr class='seqRow'> <td align='right' class='seqLabel'>Sequence:</td>";
		output += "<td class='seq'>" + seq.substring(length * i, length * (i + 1)) + "</td></tr>";

		if (pdbdata != null){
			output += "<tr class='pdbRow'> <td align='right' class='pdbLabel'> PDB_"
				+ pdbdata['pdbid'] 
				+ '_'
				+ pdbdata['chain'] +":</td>";
			var pdbstring = pdbdata['secondary'].substring(length * i, length * (i + 1))
			output += "<td class='pdb'>" + pdbstring + "</td></tr>";
		}
		else{
			var nodes = document.getElementsByClassName("enableWithPDB");
			for(var p=0; p < nodes.length; p++){
				nodes[p].style.display = 'none';
			}
		}
		//site rows
		for(var j = 0; j < sites.length; j++)
		{	
			//pred
			output += "<tr class='" + sites[j]['name'] + "prow'>";
			output += "<td align='right'>" + sites[j]['name'].toUpperCase() + " Pred:</td>";
			output += "<td class='" + sites[j] + "pred' class='pred'>";
			var predstring = sites[j]['pred'].substring(length * i, length * (i + 1));
			output += predstring + "</td></tr>";
			
			//conf
			if(sites[j]['status'] == 1) //only show conf is status is 1
			{
				output += "<tr class='" + sites[j]['name'] + "crow'>";
				output += "<td align='right'>" + sites[j]['name'].toUpperCase() + " Conf:</td>";
				output += "<td class='" + sites[j]['name'] + "conf'>" + sites[j]['conf'].substring(length * i, length * (i + 1)) + "</td></tr>"
			}
		}
		
		if(majority != null)
		{
			//majority vote row
			output += "<tr class='majrow'><td align='right'>Majority Vote:</td>";
			output += "<td class='majorityvote'>"
			var mvotestring = majority.substring(length * i, length * (i + 1));
			output += mvotestring + "</td></tr>";
		}
	}

	
	var table = document.getElementById('mytable');
	table.innerHTML = output;

	//Color code
	for (var x = 0; x < document.getElementById("mytable").rows.length; x ++){
		//document.getElementById("mytable").rows[x].cells[1].innerHTML = document.getElementById("mytable").rows[x].cells[1].textContent.replace(/(.{10})/g,"$1&nbsp;&nbsp;");
		if (document.getElementById("mytable").rows[x].cells[1].getAttribute("class") != 'seq'){
			document.getElementById("mytable").rows[x].cells[1].innerHTML = document.getElementById("mytable").rows[x].cells[1].innerHTML.replace(/E/g,'<span class="e" style="color: green;">E</span>');
			document.getElementById("mytable").rows[x].cells[1].innerHTML = document.getElementById("mytable").rows[x].cells[1].innerHTML.replace(/H/g,'<span class="h" style="color: blue;">H</span>');
			document.getElementById("mytable").rows[x].cells[1].innerHTML = document.getElementById("mytable").rows[x].cells[1].innerHTML.replace(/C/g,'<span class="c" style="color: red;">C</span>');
		}
		else {
		}
	}
}
function toggleMajority(){
	var checkBox = document.getElementById("togglemajority");
	var rows = document.getElementsByClassName("majrow");
	
	for(var i = 0; i < rows.length; i++)
	{
		if(checkBox.checked == true)
		{
			rows[i].style.display = "table-row";
		}
		else
		{
			rows[i].style.display = "none";
		}
	}
}

function togglePDB(){
	var checkBox = document.getElementById('togglepdb');
	var rows = document.getElementsByClassName('pdbRow');
	
	for(var i = 0; i < rows.length; i++)
	{
		if(checkBox.checked == true)
		{
			rows[i].style.display = "table-row";
		}
		else
		{
			rows[i].style.display = "none";
		}
	}
}
function colorizeSequence(){
	var checkBox = document.getElementById('toggleseqcolor');
	pdbData = null;
	for (var i = 0; i < a.length; i++){
		if ('pdbid' in a[i]) 
		{ 
			pdbData = a[i];
		}
	}
	if (pdbData != null){
		var seqlines = document.getElementsByClassName('seq');
		var i = 0;
		var formatedSS = pdbData['secondary'].replace(/(.{10})/g,"$1  ");
		while (i<formatedSS.length){
			for (var j = 0; j < seqlines.length; j++){
				var seqString = '';
				for(var k = 0; k < seqlines[j].textContent.length; k++){
					if(formatedSS[i] == 'E'){
						seqString += '<span class="e" style="color: green;">' + seqlines[j].textContent[k] + '</span>';
					}
					else if(formatedSS[i] == 'H'){
						seqString += '<span class="h" style="color: blue;">' + seqlines[j].textContent[k] + '</span>';
					}
					else {
						seqString += '<span class="other" style="color: black;">' + seqlines[j].textContent[k] + '</span>';
						//console.log(seqlines[j].innerHTML[k])
					}
					i++;
				}
				if (checkBox.checked == true){
					seqlines[j].innerHTML = seqString;
				}
				else{
					seqlines[j].innerHTML = seqlines[j].textContent;
				}
				
			}
		}
	}
}

function drawCounter(mySeq){
	var j=0;
	var p = 1;
	var counterstr = '';
	while (j < mySeq.length){
		if (j%10 != 0){
			//counterstr += '&nbsp;';
			counterstr += ' ';
			j = j+1;
		}
		else{
			for (var k=0; k < p.toString().length; k++){
				counterstr += p.toString()[k].toString();
				j=j+1;
			}
			p = p+10;
		}
	}
	//console.log(counterstr);
	return counterstr;
}

$('#updaterows').on('click', function() 
{
	var rownum = document.getElementById('rowfield');
	generateRows(rownum.value);
});

$('#updatecolor').on('click', function() {
	var clist = document.getElementsByClassName('c');
	for (var i = 0; i < clist.length; i++){
		clist[i].style.color =  document.getElementById("ccolor").value;
	}
	
	var elist = document.getElementsByClassName('e');
	for (var i = 0; i < elist.length; i++){
		elist[i].style.color =  document.getElementById("ecolor").value;
	}
	
	var hlist = document.getElementsByClassName('h');
	for (var i = 0; i < hlist.length; i++){
		hlist[i].style.color =  document.getElementById("hcolor").value;
	}
});

$('#genimage').on('click', function() {
	table = document.getElementById('mytable')
	html2canvas(table,{scale:1, scrollY: (window.pageYOffset * -1)}).then(function(canvas) {
	const myNode = document.getElementById("imgoutput");
	while (myNode.firstChild) {
		myNode.removeChild(myNode.firstChild);
	 }
	document.getElementById('imgoutput').append(canvas);
	});
	document.getElementById('saveimagediv').style.display = "inline";
});	

$('#genimagewlegend').on('click', function() {
	table = document.getElementById('fullresults')
	html2canvas(table,{scale:1, scrollY: (window.pageYOffset * -1)}).then(function(canvas) {
	const myNode = document.getElementById("imgoutput");
	while (myNode.firstChild) {
		myNode.removeChild(myNode.firstChild);
	 }
	document.getElementById('imgoutput').append(canvas);
	});
	document.getElementById('saveimagediv').style.display = "inline";
});

$('#saveimage').on('click', function() {
	var canvas = document.getElementsByTagName("canvas")[0];
	imglink = canvas.toDataURL("image/png", 1.0);

	var saveEle = document.createElement('a');
	saveEle.href = imglink;
	saveEle.download = "output.png";
	saveEle.click();
});	

// Display a message if user is using IE
var ua = window.navigator.userAgent;
var isIE = /MSIE|Trident/.test(ua);

if(isIE)
{
	ieDiv = document.getElementById("ieNotice");
	ieDiv.style.display = 'block';
}